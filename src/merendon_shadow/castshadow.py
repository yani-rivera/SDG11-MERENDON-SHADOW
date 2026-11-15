"""Cast shadows on a DEM for a given sun position (ray marching toward the sun)."""
import math
import numpy as np


def _shifted(dem, dcol, drow):
    """DEM sampled at (row + drow, col + dcol) with bilinear weights; NaN outside."""
    h, w = dem.shape
    c0, r0 = math.floor(dcol), math.floor(drow)
    fc, fr = dcol - c0, drow - r0
    out = np.zeros_like(dem)
    wsum = np.zeros_like(dem)
    for dr, wr in ((r0, 1 - fr), (r0 + 1, fr)):
        for dc, wc in ((c0, 1 - fc), (c0 + 1, fc)):
            wgt = wr * wc
            if wgt == 0:
                continue
            src_r0, src_r1 = max(dr, 0), min(h + dr, h)
            src_c0, src_c1 = max(dc, 0), min(w + dc, w)
            if src_r0 >= src_r1 or src_c0 >= src_c1:
                continue
            dst = (slice(src_r0 - dr, src_r1 - dr), slice(src_c0 - dc, src_c1 - dc))
            out[dst] += wgt * dem[src_r0:src_r1, src_c0:src_c1]
            wsum[dst] += wgt
    with np.errstate(invalid="ignore", divide="ignore"):
        res = out / wsum
    res[wsum < 0.999] = np.nan
    return res


def cast_shadow(dem, res, sun_alt_deg, sun_az_deg, step=None, with_exit=False):
    """Boolean array: True where the cell is in cast shadow.

    With with_exit=True also returns the height (m) at which each cell's ray
    toward the sun leaves the DEM. A sunlit cell whose ray leaves low could
    still be shaded by terrain the DEM does not cover."""
    step = step or res
    tan_alt = math.tan(math.radians(sun_alt_deg))
    az = math.radians(sun_az_deg)
    de, dn = math.sin(az), math.cos(az)          # unit vector toward the sun (east, north)
    zmax = np.nanmax(dem)
    max_dist = (zmax - np.nanmin(dem)) / tan_alt
    shadow = np.zeros(dem.shape, dtype=bool)
    exit_h = np.full(dem.shape, np.inf)
    inside = np.ones(dem.shape, dtype=bool)
    k = 1
    while k * step <= max_dist:
        dist = k * step
        samp = _shifted(dem, dist * de / res, -dist * dn / res)
        with np.errstate(invalid="ignore"):
            shadow |= samp > dem + dist * tan_alt
        if with_exit:
            left = inside & np.isnan(samp)
            exit_h[left] = (dem + dist * tan_alt)[left]
            inside &= ~left
        k += 1
    return (shadow, exit_h) if with_exit else shadow
