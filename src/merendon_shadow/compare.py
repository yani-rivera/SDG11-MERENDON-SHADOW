"""Check the r.sunmask front-line frames against shadows computed from the DEM.

For each supplied frame, report the clock time whose DEM-computed shadow
matches it best. A frame whose best match is far from its label was probably
run with a different time than its name says.
"""
from rasterio.features import rasterize
from shapely.geometry import Point

from .castshadow import cast_shadow
from .clock import label, minutes, sun_for_minute
from .inputs import load_study_area, open_dem
from .shadow_frames import shadow_polygon

COMPARE_STEP_M = 45.0   # coarser ray step than the animation: enough for matching


def computed_shadows(cfg, dem, res, first, last, step=COMPARE_STEP_M):
    """{minute: (shadow mask, sun altitude)} for every minute from first to last."""
    out = {}
    for minute in range(first, last + 1):
        alt, az = sun_for_minute(cfg, minute)
        out[minute] = (cast_shadow(dem, res, alt, az, step=step), alt)
    return out


def iou(a, b):
    return (a & b).sum() / max((a | b).sum(), 1)


def run(cfg):
    ds, dem, res = open_dem(cfg)
    layers, area, mask = load_study_area(cfg, ds)
    anchor = Point(cfg["study_area"]["lit_anchor"])

    labelled = sorted(minutes(t) for t in cfg["frames"].values())
    computed = computed_shadows(cfg, dem, res, labelled[0] - 10, labelled[-1] + 20)

    print("label   supplied %   computed % at label   best match (IoU, sun alt)   IoU at label")
    for layer, hhmm in sorted(cfg["frames"].items(), key=lambda kv: minutes(kv[1])):
        poly, _ = shadow_polygon(layers[layer][0]["geom"], area, anchor)
        theirs = rasterize([(poly, 1)], out_shape=dem.shape, transform=ds.transform,
                           fill=0).astype(bool) & mask
        b_min, (b_sh, b_alt) = max(computed.items(), key=lambda kv: iou(kv[1][0] & mask, theirs))
        mine = computed[minutes(hhmm)][0] & mask
        print(f"{hhmm}   {100 * theirs[mask].mean():6.1f}       {100 * mine[mask].mean():6.1f}"
              f"                {label(b_min)} ({iou(b_sh & mask, theirs):.2f}, {b_alt:.1f} deg)"
              f"          {iou(mine, theirs):.2f}")
