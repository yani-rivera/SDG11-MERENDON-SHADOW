"""Load config/config.toml and resolve every path against the project root."""
import hashlib
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "config" / "config.toml"


def load_config(cfg_path=None):
    """Read the TOML config. Paths in it are relative to the project root;
    they come back as absolute Path objects."""
    cfg_path = Path(cfg_path or DEFAULT_CONFIG).resolve()
    with open(cfg_path, "rb") as fh:
        cfg = tomllib.load(fh)
    cfg["dem"]["path"] = ROOT / cfg["dem"]["path"]
    cfg["source"]["gpkg"] = ROOT / cfg["source"]["gpkg"]
    cfg["paths"] = {k: ROOT / v for k, v in cfg["paths"].items()}
    cfg["_config_file"] = cfg_path
    return cfg


def sha256(path):
    """SHA-256 of a file, read in chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
