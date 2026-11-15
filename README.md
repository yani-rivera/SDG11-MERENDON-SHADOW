# When the Merendón Takes the Sun: interactive companion

Builds a single-file web page (`index.html`) that shows, minute by minute, how the
shadow of the Sierra del Merendón crosses San Pedro Sula on one afternoon.

Concept and original shadow model: Yanira A Rivera (QGIS + GRASS `r.sunmask`,
#30DayMapChallenge 2026). This pipeline recomputes the shadow from the same DEM
for every minute and packages the frames into the page.

## Layout

```
merendon-shadow-interactive/
├── config/
│   └── config.toml          all parameters and paths
├── data/                    inputs (not produced by the pipeline)
│   ├── dem16m.tiff
│   └── shadow.gpkg
├── scripts/                 entry points, run from anywhere
│   ├── run_all.py           render_frames + build_page
│   ├── render_frames.py
│   ├── build_page.py
│   └── compare_frames.py
├── src/merendon_shadow/     the library
├── templates/
│   └── template.html        the page: map, time slider, readouts, chart
└── output/                  everything the pipeline writes
    ├── frames.json
    └── index.html
```

## Inputs (put them in `data/`)

| File | What it is |
|---|---|
| `data/dem16m.tiff` | Elevation model, projected CRS in metres (EPSG:32616). Copernicus GLO-30 via OpenTopography. |
| `data/shadow.gpkg` | GeoPackage with the city frame polygon and the `r.sunmask` front lines. |

Paths, date, time window, landmark and thresholds are all in `config/config.toml`.
Paths in the config are relative to the project root.

## Run

```
pip install -r requirements.txt
python scripts/run_all.py          # DEM -> output/frames.json -> output/index.html
python scripts/compare_frames.py   # optional check of the front-line frames against the DEM
```

The steps can also run one at a time (`scripts/render_frames.py`, then
`scripts/build_page.py`). Every script takes an optional config path, so a
second configuration (another date, another city) can sit next to the first:
`python scripts/run_all.py config/another.toml`.

`output/index.html` is self-contained (only the fonts load from the web) and can be
published with GitHub Pages as it is.

## Modules (`src/merendon_shadow/`)

| File | Role |
|---|---|
| `config.py` | Loads the config, resolves paths against the project root, file hashes. |
| `clock.py` | Clock times ↔ minutes; sun position for a minute on the configured date. |
| `solar.py` | Sun altitude and azimuth (NOAA approximation). |
| `castshadow.py` | Cast shadow on a DEM by ray marching toward the sun; also reports where each ray leaves the DEM. |
| `gpkgio.py` | Reads GeoPackage layers without GDAL. |
| `inputs.py` | Opens the DEM and builds the study-area mask (shared by render and compare). |
| `shadow_frames.py` | Study area and filled shadow polygons from front lines. |
| `imaging.py` | Hillshade base image and per-minute shadow overlays. |
| `provenance.py` | Provenance record for `frames.json` and the page footer. |
| `render.py` | Runs the animation frames and writes `frames.json`. |
| `page.py` | Injects `frames.json` into the template. |
| `compare.py` | Matches each front-line frame to the best-fitting clock time. |

## Method

For each minute, every DEM cell looks toward the sun. If terrain along that
line rises above the ray, the cell is in shadow. The sun position is computed
for the landmark in `config.toml`.

Three states are drawn:

- **In shadow**: terrain inside the DEM blocks the sun.
- **In sun**: the ray leaves the DEM above `outside_terrain_max_m`.
- **Can't tell**: the cell is sunlit inside the DEM, but its ray leaves the DEM
  below `outside_terrain_max_m`, so terrain outside the data could still shade it.

## Known limits (version 0.3.0)

- The DEM ends at the southern edge of the city and about 11.5 km west of
  Parque Central. Between 16% and 25% of the city frame is "can't tell".
  A DEM extended about 20 km west and 15 km south removes most of it
  (box: W -88.32, E -87.89, S 15.31, N 15.63).
- `outside_terrain_max_m = 2300` is an assumption to verify.
- Zero-valued cells along the DEM's ragged edges (from reprojection) are used as they are.
- `scripts/compare_frames.py` on the 13 Nov 2026 data: seven front-line frames match their
  own time; the layer labelled 16:50 matches 17:00 (IoU 0.94) and should be rerun or relabelled.
- The date comes from the layer names (16 November 2026). Confirm it against the poster.

## Security and phones

- The page is static: no forms, cookies, tracking or calls to other servers. The only
  outside request is for the Google Fonts.
- A Content-Security-Policy in the page allows only its own inline script (by SHA-256 hash,
  filled in by `build_page.py`), images from inside the page, and the Google Fonts.
  It also sends no referrer. GitHub Pages can't set response headers, so the policy sits in
  a `<meta>` tag, which means it can't block other sites from framing the page.
- The data is embedded with `<`, `>` and `&` escaped, so no text in the config (a title,
  a citation) can break out of the script.
- On phones the map stays pinned at the top while you drag the slider, and the map labels
  and markers are enlarged so they stay readable when the map is drawn small.

## Provenance

`output/frames.json` records the DEM, GeoPackage and config file names with their
SHA-256 hashes, CRS, script name and version, build time (UTC), sun model and ray step.
The page footer shows the DEM, CRS, script version, build time, sun model and ray step.

Version 0.3.0 reorganised the folders (config, data, scripts, src, templates, output)
and added the GeoPackage and config hashes to the provenance. It also added the
Content-Security-Policy, safe embedding of the data, phone layout fixes, and tick labels
read from the data (they followed the 16:15–17:00 window before). The shadow frames are
unchanged from 0.2.0 for the same inputs.

## Sources

European Space Agency (2024). Copernicus Global Digital Elevation Model.
Distributed by OpenTopography. https://doi.org/10.5069/G9028PQB
