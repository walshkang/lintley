#!/usr/bin/env python3
import sys, json
input_text = sys.stdin.read()
# Simple responder: if Observer present, emit a CAUTION payload; if Actor present, emit Actor payload; otherwise echo ok
if "Observer" in input_text or "SliceObserver" in input_text:
    payload = {
        "verdict": "CAUTION",
        "findings": ["Potential data leak: uses secrets"],
        "risk_level": "high",
        "recommended_changes": "Do not include credentials in patches.",
        "metadata": {"model": "fake-local-llm"}
    }
    print(json.dumps(payload))
elif "Actor" in input_text or "SliceActor" in input_text:
    payload = {
        "analysis": "Propose a change but includes sensitive snippet.",
        "patch": "diff --git a/secret.txt b/secret.txt\n--- a/secret.txt\n+++ b/secret.txt\n@@ -1 +1 @@\n-secret\n+REDACTED\n",
        "instructions": "Apply patch",
        "confidence": "low",
        "metadata": {"model": "fake-local-llm"}
    }
    print(json.dumps(payload))
else:
    print(json.dumps({"ok": True}))
