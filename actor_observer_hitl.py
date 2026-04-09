#!/usr/bin/env python3
"""
Actor-Observer-HITL Prototype with Multi-Provider Support

Supports: Anthropic, Google Generative AI, OpenAI
Auto-detects provider from API key and lists available models.

Architecture:
- Actor Agent: Completes the primary task
- Observer Agent: Audits Actor's work for hallucinations/goal drift
- HITL Checkpoint: Asks human for approval before execution

Flow: API Setup → Task → Actor → Observer → [Risk Assessment] → HITL Gate → Execute
"""

import json
import sys
import os
from typing import TypedDict, Optional

# Provider imports (lazy-loaded)
anthropic = None
google_generativeai = None
openai = None


class AgentResponse(TypedDict):
    role: str
    content: str
    reasoning: str


class ProviderClient:
    """Abstraction layer for different LLM providers."""

    def __init__(self, provider: str, api_key: str, model: str):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self._init_provider()

    def _init_provider(self):
        """Initialize the appropriate provider SDK."""
        if self.provider == "anthropic":
            global anthropic
            import anthropic as anthropic_module
            anthropic = anthropic_module
            self.client = anthropic.Anthropic(api_key=self.api_key)
        elif self.provider == "google":
            global google_generativeai
            import google.generativeai as genai_module
            google_generativeai = genai_module
            google_generativeai.configure(api_key=self.api_key)
        elif self.provider == "openai":
            global openai
            import openai as openai_module
            openai = openai_module
            self.client = openai_module.OpenAI(api_key=self.api_key)

    def generate(self, system_prompt: str, user_message: str, max_tokens: int = 1000) -> str:
        """Generate response using the configured provider."""
        if self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return response.content[0].text

        elif self.provider == "google":
            model = google_generativeai.GenerativeModel(
                self.model,
                system_instruction=system_prompt,
            )
            response = model.generate_content(
                user_message,
                generation_config=google_generativeai.types.GenerationConfig(
                    max_output_tokens=max_tokens
                ),
            )
            return response.text

        elif self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return response.choices[0].message.content

    @staticmethod
    def detect_provider(api_key: str) -> str:
        """Detect provider from API key format."""
        api_key_prefix = api_key[:3].lower()

        # Anthropic keys start with "sk-ant-"
        if api_key.startswith("sk-ant-"):
            return "anthropic"
        # OpenAI keys start with "sk-"
        elif api_key.startswith("sk-"):
            return "openai"
        # Google keys are usually long alphanumeric or have AIza prefix
        elif api_key.startswith("AIza") or len(api_key) > 100:
            return "google"
        else:
            return None

    @staticmethod
    def list_models(provider: str, api_key: str) -> list:
        """List available models for the provider."""
        if provider == "anthropic":
            import anthropic as anthropic_module
            # Anthropic has known models
            return [
                "claude-opus-4-6",
                "claude-sonnet-4-6",
                "claude-haiku-4-5-20251001",
            ]

        elif provider == "google":
            import google.generativeai as genai_module
            genai_module.configure(api_key=api_key)
            try:
                models = genai_module.list_models()
                # Filter to text-generation models
                available = []
                for m in models:
                    if "generateContent" in m.supported_generation_methods:
                        available.append(m.name.split("/")[-1])
                return available[:10]  # Return first 10
            except Exception as e:
                print(f"Error listing Google models: {e}")
                return ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"]

        elif provider == "openai":
            import openai as openai_module
            client = openai_module.OpenAI(api_key=api_key)
            try:
                models = client.models.list()
                # Filter to gpt models
                return [m.id for m in models if "gpt" in m.id][:10]
            except Exception as e:
                print(f"Error listing OpenAI models: {e}")
                return ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]


def setup_provider() -> ProviderClient:
    """Configure provider from environment, .env.local, or interactively.

    Returns a ready ProviderClient instance when possible.
    """
    print("\n" + "=" * 80)
    print("🔧 PROVIDER SETUP")
    print("=" * 80)

    # Try environment first
    detected_provider = os.environ.get("HITL_PROVIDER")
    api_key = os.environ.get("HITL_API_KEY")
    selected_model = os.environ.get("HITL_MODEL")

    # Fallback to .env.local
    env_file = Path(".env.local")
    if env_file.exists():
        try:
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k == "HITL_PROVIDER" and not detected_provider:
                        detected_provider = v
                    elif k == "HITL_API_KEY" and not api_key:
                        api_key = v
                    elif k == "HITL_MODEL" and not selected_model:
                        selected_model = v
        except Exception:
            pass

    # If we have an API key but no provider, try auto-detection
    if api_key and not detected_provider:
        detected_provider = ProviderClient.detect_provider(api_key)

    if detected_provider and api_key:
        print(f"✅ Using provider from env/config: {detected_provider.upper()}")
        print("⏳ Initializing provider...")
        try:
            client = ProviderClient(detected_provider, api_key, selected_model or "")
            print("✅ Provider initialized successfully!\n")
            return client
        except Exception as e:
            print(f"❌ Failed to initialize provider: {e}")
            # Fall through to interactive prompt

    # Interactive fallback (unchanged behavior)
    # Get API key
    print("\nEnter your API key (supports: Anthropic, Google Generative AI, OpenAI)")
    print("(Your key will NOT be saved or logged)")
    api_key = input("\n🔑 API Key: ").strip()

    if not api_key:
        print("❌ No API key provided.")
        sys.exit(1)

    # Detect provider
    detected_provider = ProviderClient.detect_provider(api_key)

    if detected_provider:
        print(f"\n✅ Detected provider: {detected_provider.upper()}")
    else:
        print("\n⚠️  Could not auto-detect provider. Which one are you using?")
        print("  [1] Anthropic")
        print("  [2] Google Generative AI")
        print("  [3] OpenAI")
        choice = input("\nChoose [1-3]: ").strip()
        provider_map = {"1": "anthropic", "2": "google", "3": "openai"}
        detected_provider = provider_map.get(choice)
        if not detected_provider:
            print("❌ Invalid choice.")
            sys.exit(1)
        print(f"✅ Using provider: {detected_provider.upper()}")

    # List available models
    print("\n⏳ Fetching available models...")
    try:
        models = ProviderClient.list_models(detected_provider, api_key)
        if not models:
            print("❌ Could not fetch models.")
            sys.exit(1)
    except Exception as e:
        print(f"⚠️  Error fetching models: {e}")
        models = []

    if models:
        print(f"\n📦 Available models ({len(models)} shown):")
        for i, model in enumerate(models[:10], 1):
            print(f"  [{i}] {model}")

        choice = input("\nSelect model [1-10] (or press Enter for #1): ").strip()
        try:
            idx = int(choice) - 1 if choice else 0
            selected_model = models[idx]
        except (ValueError, IndexError):
            selected_model = models[0]
        print(f"✅ Using model: {selected_model}")
    else:
        # Manual model input if fetch failed
        selected_model = input("\nEnter model name manually: ").strip()
        if not selected_model:
            print("❌ No model provided.")
            sys.exit(1)

    # Create and test client
    print("\n⏳ Initializing provider...")
    try:
        client = ProviderClient(detected_provider, api_key, selected_model)
        print("✅ Provider initialized successfully!\n")
        return client
    except Exception as e:
        print(f"❌ Failed to initialize provider: {e}")
        sys.exit(1)


def actor_agent(provider: ProviderClient, task: str, context: str = "") -> AgentResponse:
    """
    The Actor Agent performs the primary task.
    It generates a solution and exposes its reasoning.
    """
    system_prompt = """You are the Actor Agent. Your job is to complete the assigned task thoroughly and carefully.

IMPORTANT: Always structure your response with:
1. ANALYSIS: Your step-by-step thinking
2. DECISION: Your final decision/solution
3. CONFIDENCE: Your confidence level (high/medium/low) and any caveats

Be explicit about assumptions you're making and limitations you're aware of."""

    user_message = f"Task: {task}\n\nContext: {context}" if context else f"Task: {task}"

    content = provider.generate(system_prompt, user_message, max_tokens=1000)
    return {
        "role": "Actor",
        "content": content,
        "reasoning": extract_section(content, "ANALYSIS"),
    }


def observer_agent(
    provider: ProviderClient, task: str, actor_response: AgentResponse
) -> AgentResponse:
    """
    The Observer Agent audits the Actor's work.
    It checks for hallucinations, goal drift, logical errors, and risky assumptions.
    """
    system_prompt = """You are the Observer Agent - a critical auditor of another AI's work.

Your job is to:
1. Check if the Actor understood the task correctly
2. Identify any logical flaws or unsupported claims
3. Detect hallucinations (false facts presented as truth)
4. Flag risky assumptions or edge cases not considered
5. Assess overall quality and likelihood of success

Structure your response as:
1. AUDIT_SUMMARY: Overall assessment (PASS/CAUTION/FAIL)
2. FINDINGS: List specific issues (if any)
3. RISK_LEVEL: high/medium/low
4. RECOMMENDATION: Should this proceed to human review?

Be thorough but fair. The Actor did its best - focus on what matters."""

    user_message = f"""Audit this work:

ORIGINAL TASK: {task}

ACTOR'S RESPONSE:
{actor_response['content']}

Is the Actor's work sound? What risks or errors do you see?"""

    content = provider.generate(system_prompt, user_message, max_tokens=800)
    return {
        "role": "Observer",
        "content": content,
        "reasoning": extract_section(content, "AUDIT_SUMMARY"),
    }


def extract_risk_level(observer_response: str) -> str:
    """Extract risk level from Observer's assessment."""
    for line in observer_response.split("\n"):
        if "RISK_LEVEL" in line or "risk" in line.lower():
            if "high" in line.lower():
                return "high"
            elif "medium" in line.lower():
                return "medium"
            elif "low" in line.lower():
                return "low"
    return "medium"  # Default


def extract_section(text: str, section_name: str) -> str:
    """Extract a named section from agent response."""
    lines = text.split("\n")
    in_section = False
    result = []
    for line in lines:
        if section_name in line:
            in_section = True
            continue
        if in_section:
            if line.startswith(("1.", "2.", "3.", "4.", "5.")) or (
                any(s in line for s in ["ANALYSIS", "DECISION", "AUDIT", "RISK", "FINDING"])
            ):
                break
            result.append(line)
    return "\n".join(result).strip()


def hitl_checkpoint(
    task: str, actor_response: AgentResponse, observer_response: AgentResponse, risk_level: str
) -> dict:
    """
    Human-in-the-Loop Checkpoint.
    Presents the situation and asks for human approval.
    """
    print("\n" + "=" * 80)
    print("🚨 HUMAN-IN-THE-LOOP CHECKPOINT 🚨")
    print("=" * 80)

    print(f"\n📋 ORIGINAL TASK:\n{task}\n")

    print("─" * 80)
    print("👤 ACTOR'S PROPOSAL:")
    print("─" * 80)
    print(actor_response["content"])

    print("\n" + "─" * 80)
    print("🔍 OBSERVER'S AUDIT:")
    print("─" * 80)
    print(observer_response["content"])

    print("\n" + "─" * 80)
    risk_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}[risk_level]
    print(f"\n⚠️  RISK LEVEL: {risk_color} {risk_level.upper()}")
    print("─" * 80)

    print("\n📝 OPTIONS:")
    print("  [a] APPROVE - Proceed with Actor's proposal")
    print("  [r] REJECT - Stop here, don't execute")
    print("  [m] MODIFY - Request changes (describe below)")
    print()

    while True:
        choice = input("Your decision [a/r/m]: ").strip().lower()
        if choice in ["a", "r", "m"]:
            break
        print("Invalid choice. Enter 'a', 'r', or 'm'.")

    approval_data = {"decision": choice, "modification_request": None}

    if choice == "m":
        modification = input("\nDescribe the changes needed:\n> ")
        approval_data["modification_request"] = modification

    return approval_data


def run_workflow(provider: ProviderClient, task: str, context: str = "", allow_auto_approve: bool = False):
    """
    Run the full Actor-Observer-HITL workflow.
    """
    print("\n" + "=" * 80)
    print("🤖 ACTOR-OBSERVER-HITL WORKFLOW")
    print("=" * 80)
    print(f"\n📌 Task: {task}")
    print(f"🔧 Provider: {provider.provider.upper()} | Model: {provider.model}\n")

    # Step 1: Actor does the work
    print("⏳ Actor Agent is analyzing...")
    actor_response = actor_agent(provider, task, context)
    print("✅ Actor complete.\n")

    # Step 2: Observer audits
    print("⏳ Observer Agent is auditing...")
    observer_response = observer_agent(provider, task, actor_response)
    print("✅ Observer complete.\n")

    # Step 3: Determine risk level
    risk_level = extract_risk_level(observer_response["content"])

    # Step 4: HITL checkpoint
    if allow_auto_approve and risk_level == "low":
        print(f"✅ Risk level is LOW - auto-approving.")
        approval = {"decision": "a", "modification_request": None}
    else:
        approval = hitl_checkpoint(task, actor_response, observer_response, risk_level)

    # Step 5: Execute based on approval
    print("\n" + "=" * 80)
    if approval["decision"] == "a":
        print("✅ APPROVED - Executing Actor's proposal")
        print("=" * 80)
        return {
            "status": "approved",
            "actor_work": actor_response["content"],
            "observer_review": observer_response["content"],
            "risk_level": risk_level,
        }
    elif approval["decision"] == "r":
        print("❌ REJECTED - Workflow stopped")
        print("=" * 80)
        return {"status": "rejected", "reason": "Human rejected the proposal"}
    else:  # modify
        print("🔄 MODIFICATION REQUESTED")
        print("=" * 80)
        print(f"Requested changes: {approval['modification_request']}")
        return {
            "status": "modification_requested",
            "modification": approval["modification_request"],
        }


if __name__ == "__main__":
    # Step 1: Setup provider interactively
    provider = setup_provider()

    # Step 2: Example task
    task = "Review this code for security vulnerabilities and propose fixes."
    context = """
    def process_user_input(user_input):
        query = "SELECT * FROM users WHERE id = " + user_input
        conn.execute(query)
        return redirect(f"/{user_input}")
    """

    result = run_workflow(provider, task, context, allow_auto_approve=False)

    # Step 3: Show result
    print("\n" + "=" * 80)
    print("📊 FINAL RESULT")
    print("=" * 80)
    print(json.dumps(result, indent=2, default=str))
