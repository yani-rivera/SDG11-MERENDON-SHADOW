"""Open the DEM and build the study-area mask (shared by render and compare)."""
import rasterio
from rasterio.features import rasterize

from .gpkgio import read_layers
from .shadow_frames import study_area


def open_dem(cfg):
    """Dataset, elevation array (float64) and cell size in metres."""
    ds = rasterio.open(cfg["dem"]["path"])
    return ds, ds.read(1).astype("float64"), ds.res[0]


def load_study_area(cfg, ds):
    """GeoPackage layers, the study-area polygon and its boolean mask on the DEM grid."""
    layers = read_layers(cfg["source"]["gpkg"])
    area = study_area(layers[cfg["source"]["city_layer"]][0]["geom"],
                      cfg["study_area"]["x_max"], cfg["study_area"]["y_min"])
    mask = rasterize([(area, 1)], out_shape=(ds.height, ds.width),
                     transform=ds.transform, fill=0).astype(bool)
    return layers, area, mask
