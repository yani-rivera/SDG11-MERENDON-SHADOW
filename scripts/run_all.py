#!/usr/bin/env python3
"""Run the full build: render the frames, then build the page.

Usage: python scripts/run_all.py [path/to/config.toml]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from merendon_shadow.config import load_config  # noqa: E402
from merendon_shadow import page, render  # noqa: E402

if __name__ == "__main__":
    cfg = load_config(sys.argv[1] if len(sys.argv) > 1 else None)
    render.run(cfg)
    page.run(cfg)
