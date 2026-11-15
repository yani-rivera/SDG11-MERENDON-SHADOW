"""Turn shadow front lines (clipped to a study area) into filled shadow polygons.

The fronts are boundaries of the shadow mask, so each one splits the study
area into faces. The face that holds a known sunlit anchor point is "light";
every other face is "shadow".
"""
import math
from shapely.geometry import LineString, MultiLineString, Point, box
from shapely.ops import polygonize, unary_union


def study_area(city_polygon, x_max, y_min):
    """City frame cut at the east and south limits of the shadow raster."""
    minx, _, _, maxy = city_polygon.bounds
    return city_polygon.intersection(box(minx - 1, y_min, x_max, maxy + 1))


def _outside_point(pt, area, radius=2.0):
    """A point `radius` metres from pt that lies outside the study area."""
    best, best_d = None, -1.0
    for i in range(16):
        a = 2 * math.pi * i / 16
        cand = Point(pt[0] + radius * math.cos(a), pt[1] + radius * math.sin(a))
        if not area.contains(cand):
            d = cand.distance(area)
            if d > best_d:
                best, best_d = cand, d
    return best


def _extend(line, area, tol=1.0):
    """Push line ends that sit on the area boundary slightly past it,
    so they node cleanly with the boundary."""
    coords = list(line.coords)
    for idx in (0, -1):
        p = coords[idx]
        if Point(p).distance(area.boundary) < tol:
            out = _outside_point(p, area)
            if out is not None:
                if idx == 0:
                    coords.insert(0, (out.x, out.y))
                else:
                    coords.append((out.x, out.y))
    return LineString(coords)


def shadow_polygon(front, area, lit_anchor):
    """Shadow part of the study area for one front (MultiLineString)."""
    clipped = front.intersection(area)
    geoms = getattr(clipped, "geoms", [clipped])
    parts = [_extend(p, area) for p in geoms
             if p.geom_type == "LineString" and len(p.coords) >= 2]
    noded = unary_union([area.boundary] + parts)
    faces = [f for f in polygonize(noded)
             if area.buffer(0.5).contains(f.representative_point())]
    shadow = unary_union([f for f in faces if not f.contains(lit_anchor)])
    return shadow, len(faces)
