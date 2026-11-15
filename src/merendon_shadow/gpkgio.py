"""Read geometries from a GeoPackage without GDAL (GPKG blob header + WKB)."""
import sqlite3, struct
from shapely import wkb

def _strip_header(blob):
    flags = blob[3]
    env = (flags >> 1) & 0x07
    env_len = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}[env]
    return blob[8 + env_len:]

def _ident(name):
    """Quote an SQLite identifier (table names come from the file itself)."""
    return '"' + name.replace('"', '""') + '"'

def read_layers(path):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    out = {}
    for (t,) in con.execute("select table_name from gpkg_contents").fetchall():
        cols = [c[1] for c in con.execute(f"pragma table_info({_ident(t)})")]
        rows = con.execute(f"select * from {_ident(t)}").fetchall()
        feats = []
        for r in rows:
            d = dict(zip(cols, r))
            d["geom"] = wkb.loads(_strip_header(d["geom"]))
            feats.append(d)
        out[t] = feats
    return out
