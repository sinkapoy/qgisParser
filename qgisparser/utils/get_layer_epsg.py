import qgis.core as core

def get_layer_epsg(layer: core.QgsRasterLayer):
    crs = layer.crs()
    id = crs.toWkt(
        core.QgsCoordinateReferenceSystem.WktVariant.WKT2_2019_SIMPLIFIED)
    id = "epsg:" + id.split("ID[")[-1].split(",")[-1].replace("]", "")
    return id