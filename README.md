GitHub synchronization configured.

## Local scene reports

`create_scene_report` runs the validated local GeoTIFF workflow and returns a
small JSON-ready NDWI summary. It includes the water-detection measurements,
input band filenames, and spatial extent, while deliberately excluding raster
arrays. This keeps the first real-scene interface offline, portable, and safe
to persist without downloading or modifying satellite data.
