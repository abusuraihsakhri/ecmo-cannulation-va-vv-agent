"""Static browser smoke tests without requiring a running server."""
from pathlib import Path
import re
import shutil
import subprocess

import pytest

WEB = Path(__file__).resolve().parents[1] / "web" / "index.html"


def test_static_browser_experience_is_honestly_labeled():
    html = WEB.read_text(encoding="utf-8")
    assert "Not for clinical use." in html
    assert "No API, account, remote model" in html
    assert "URL.createObjectURL" in html
    assert "fetch(" not in html
    assert "Math.random" not in html
    assert 'audit_signature: null' in html


def test_embedded_javascript_syntax():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js not installed; JS parse check unavailable")
    html = WEB.read_text(encoding="utf-8")
    match = re.search(r"<script>(.*?)</script>", html, flags=re.S)
    assert match, "Expected an embedded browser script"
    result = subprocess.run(
        [node, "--check", "-"], input=match.group(1), text=True,
        capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
