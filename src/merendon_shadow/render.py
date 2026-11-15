"""Compute minute-by-minute shadow frames from the DEM and write frames.json."""
import json

from pyproj import Transformer

from .castshadow import cast_shadow
from .clock import label, minutes, sun_for_minute
from .imaging import base_image, frame_image
from .inputs import load_study_area, open_dem
from .provenance import build_provenance


def _to_px(ds, res):
    """Projected (x, y) -> fractional (col, row) on the DEM grid."""
    def px(x, y):
        return [round((x - ds.bounds.left) / res, 1), round((ds.bounds.top - y) / res, 1)]
    return px


def render_frame(cfg, dem, res, minute, mask, lm_rc):
    """One animation frame: sun position, shares of the city frame, landmark state, overlay."""
    alt, az = sun_for_minute(cfg, minute)
    shadow, exit_h = cast_shadow(dem, res, alt, az, step=cfg["animation"]["ray_step_m"], with_exit=True)
    unsure = (~shadow) & (exit_h < cfg["animation"]["outside_terrain_max_m"])
    r, c = lm_rc
    state = "shadow" if shadow[r, c] else ("unsure" if unsure[r, c] else "sun")
    return {
        "time": label(minute),
        "sun_alt": round(alt, 1), "sun_az": round(az, 1),
        "shadow_pct": round(100 * shadow[mask].mean(), 1),
        "unsure_pct": round(100 * unsure[mask].mean(), 1),
        "landmark": state,
        "img": frame_image(shadow, unsure),
    }


def run(cfg):
    ds, dem, res = open_dem(cfg)
    _, city, mask = load_study_area(cfg, ds)
    px = _to_px(ds, res)

    to_utm = Transformer.from_crs(4326, ds.crs.to_epsg(), always_xy=True)
    lm_xy = to_utm.transform(cfg["landmark"]["lon"], cfg["landmark"]["lat"])
    lm_c, lm_r = (int(v) for v in px(*lm_xy))

    frames = []
    for minute in range(minutes(cfg["animation"]["start"]), minutes(cfg["animation"]["end"]) + 1):
        f = render_frame(cfg, dem, res, minute, mask, (lm_r, lm_c))
        frames.append(f)
        print(f["time"], f["sun_alt"], f["shadow_pct"], f["unsure_pct"], f["landmark"],
              len(f["img"]) // 1024, "KB", flush=True)

    data = {
        "title": cfg["project"]["title"],
        "date": cfg["sun"]["date"],
        "raster": {"width": ds.width, "height": ds.height, "metres_per_px": round(res, 3)},
        "base": base_image(dem, res),
        "city_frame": [px(x, y) for x, y in city.exterior.coords],
        "city_km2": round(city.area / 1e6),
        "landmark": {"name": cfg["landmark"]["name"], "px": px(*lm_xy)},
        "outside_terrain_max_m": cfg["animation"]["outside_terrain_max_m"],
        "frames": frames,
        "provenance": build_provenance(cfg, ds),
    }
    out = cfg["paths"]["frames_json"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, separators=(",", ":")))
    print(out.name, out.stat().st_size // 1024, "KB")
