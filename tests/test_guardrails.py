from guardrails.monitor import detect_risky_command


def test_detect_rm_rf():
    cmd = "rm -rf /tmp/somedir"
    score, reasons = detect_risky_command(cmd)
    assert score > 0
    assert any("rm -rf" in r or "recursive" in r for r in reasons)


def test_detect_mkfs():
    cmd = "mkfs.ext4 /dev/sdb"
    score, reasons = detect_risky_command(cmd)
    assert score > 0
    assert any("mkfs" in r for r in reasons)


def test_benign_command():
    cmd = "echo hello world"
    score, reasons = detect_risky_command(cmd)
    assert score == 0
    assert reasons == []
