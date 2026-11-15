"""Images embedded in the page: hillshade base and per-minute shadow overlays."""
import base64
import io

import numpy as np
from PIL import Image

SHADOW, UNSURE = 1, 2


def hillshade(dem, res, az=315.0, alt=45.0, z=1.6):
    gy, gx = np.gradient(dem * z, res)
    slope = np.pi / 2 - np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)
    a, h = np.radians(360 - az + 90), np.radians(alt)
    hs = np.sin(h) * np.sin(slope) + np.cos(h) * np.cos(slope) * np.cos(a - np.pi / 2 - aspect)
    return np.clip(hs, 0, 1)


def _data_uri(im, fmt, mime, **save_kw):
    buf = io.BytesIO()
    im.save(buf, format=fmt, **save_kw)
    return f"data:{mime};base64," + base64.b64encode(buf.getvalue()).decode()


def base_image(dem, res):
    """Warm grey hillshade as a JPEG data URI."""
    grey = 150 + 100 * hillshade(dem, res)
    rgb = np.stack([grey * 1.0, grey * 0.965, grey * 0.84], axis=-1).clip(0, 255).astype("uint8")
    return _data_uri(Image.fromarray(rgb), "JPEG", "image/jpeg", quality=82, optimize=True)


def frame_image(shadow, unsure):
    """Shadow (solid) and can't-tell (hatched) cells as a paletted PNG data URI."""
    h, w = shadow.shape
    idx = np.zeros((h, w), dtype="uint8")
    rr, cc = np.indices((h, w))
    idx[unsure & (((rr + cc) % 6) < 2)] = UNSURE
    idx[shadow] = SHADOW
    im = Image.fromarray(idx, mode="P")
    im.putpalette([0, 0, 0, 16, 19, 28, 96, 98, 106] + [0] * (253 * 3))
    return _data_uri(im, "PNG", "image/png", optimize=True, transparency=bytes([0, 214, 200]))
