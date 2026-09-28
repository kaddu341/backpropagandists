"""Runs the landing-page physics tests (landscape.test.mjs) under Node, so `uv run pytest` covers them."""

import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
def test_landscape_js():
    subprocess.run(["node", "--test", str(Path(__file__).with_name("landscape.test.mjs"))], check=True)
