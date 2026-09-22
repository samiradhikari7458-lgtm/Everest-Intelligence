GitHub synchronization configured.

## Local scene reports

`create_scene_report` runs the validated local GeoTIFF workflow and returns a
small JSON-ready NDWI summary. It includes the water-detection measurements,
input band filenames, and spatial extent, while deliberately excluding raster
arrays. This keeps the first real-scene interface offline, portable, and safe
to persist without downloading or modifying satellite data.

### Run a local scene report

With the project environment active, provide a matched pair of local GeoTIFF
bands and a stable scene identifier:

```bash
python -m src.everest_intelligence.scene_cli \
  --green path/to/green.tif \
  --nir path/to/nir.tif \
  --scene-id nepal-water-2026-01 \
  --threshold 0.20
```

The command writes the JSON report to the terminal. It only reads the supplied
files; it never fetches data or changes the GeoTIFFs.
