#!/usr/bin/env python3
"""Optional check: match each r.sunmask front-line frame to its best-fitting clock time.

Usage: python scripts/compare_frames.py [path/to/config.toml]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from merendon_shadow.config import load_config  # noqa: E402
from merendon_shadow import compare  # noqa: E402

if __name__ == "__main__":
    cfg = load_config(sys.argv[1] if len(sys.argv) > 1 else None)
    compare.run(cfg)
