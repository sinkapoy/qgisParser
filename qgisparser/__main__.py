import qgis.core as core
from .process_raster_layer import multiband_layer_image
from .utils.settings import Settings

threads = 4

settings = Settings()
settings.chunk_size = 256
settings.sample_per_m = 4
print("settings:", settings)
print("==========")
core.QgsApplication.setPrefixPath("/usr/bin/qgis", True)
app = core.QgsApplication([], False)
project = core.QgsProject.instance()
project.read(settings.project_path)

print("==========")
mapLayers = project.layerStore().mapLayers()

def process_layer(layer: core.QgsRasterLayer):
    print(layer.renderer().type())
    r_type = layer.renderer().type()

    if (str(r_type) == "multibandcolor"):
        return multiband_layer_image(layer, settings)
    pass


for key in mapLayers:
    layer: core.QgsRasterLayer = mapLayers[key]
    if (layer.type() == core.QgsMapLayerType.RasterLayer):
        process_layer(layer)


app.exit()
import os
os.system("rm -rf ./https:")