"""Runs the landing-page physics tests (landscape.test.mjs) under Node, so `uv run pytest` covers them."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest


# Skip locally without Node, but never in CI: a missing Node there must fail, not pass silently.
@pytest.mark.skipif(shutil.which("node") is None and not os.environ.get("CI"), reason="Node.js is not installed")
def test_landscape_js():
    subprocess.run(["node", "--test", str(Path(__file__).with_name("landscape.test.mjs"))], check=True)
