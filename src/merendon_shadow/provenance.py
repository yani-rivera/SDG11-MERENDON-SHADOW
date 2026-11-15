"""Provenance record written into frames.json and shown in the page footer."""
from datetime import datetime, timezone

from .config import ROOT, sha256


def build_provenance(cfg, ds):
    dem, gpkg, conf = cfg["dem"]["path"], cfg["source"]["gpkg"], cfg["_config_file"]
    return {
        "dem_file": dem.name,
        "dem_sha256": sha256(dem),
        "dem_citation": cfg["dem"]["citation"],
        "gpkg_file": gpkg.name,
        "gpkg_sha256": sha256(gpkg),
        "config_file": str(conf.relative_to(ROOT)) if conf.is_relative_to(ROOT) else conf.name,
        "config_sha256": sha256(conf),
        "crs": str(ds.crs),
        "script": cfg["project"]["name"],
        "script_version": cfg["project"]["script_version"],
        "built_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "sun_model": "NOAA solar position approximation at the landmark",
        "ray_step_m": cfg["animation"]["ray_step_m"],
    }
