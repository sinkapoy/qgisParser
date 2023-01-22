import httplib2
import time
import qgis.core as core
from pyproj import Proj, transform as proj_transform
from .utils.get_layer_epsg import *
import math
from PIL.Image import open as open_image
import os.path
from .utils.settings import Settings
import json



__c = httplib2.Http("https://ru-ru.topographic-map.com", )
__headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Connection': 'keep-alive',
    'Cookie': 'cookies=%7B%22analytics%22%3Atrue%2C%22advertisements%22%3Atrue%7D',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}

def __getTileHeight(southLatitude: float, westLongtitute: float, northLatitude: float, eastLongitude: float, name: str):
    # https://ru-ru.topographic-map.com/?_path=api.maps.getOverlay&southLatitude=0&westLongitude=0&northLatitude=61.69013888888889&eastLongitude=105.2713888888889&zoom=6&version=202212101952
    #     print("GET", southLatitude, westLongtitute, northLatitude, eastLongitude)
    time.sleep(1)
    result = __c.request("https://ru-ru.topographic-map.com/?_path=api.maps.getOverlay&southLatitude={0}&westLongitude={1}&northLatitude={2}&eastLongitude={3}&zoom=20&version=202212101952&minimum=0&maximum=6000".format(southLatitude, westLongtitute, northLatitude, eastLongitude), method="GET", headers=__headers)
    if(result[0]['status'] == '200'):
        file = open(name + ".jpg", "wb")
        file.write(result[1])

def process_layer_height(layer: core.QgsRasterLayer, settings: Settings):
    layer_name = layer.name()
    max_height_tile_size = settings.height_settings.max_ack_tile_size
    extent: core.QgsRectangle = layer.extent()
    inProj = Proj(get_layer_epsg(layer))
    outProj = Proj('epsg:4326')

    x_size = extent.xMaximum() - extent.xMinimum()
    y_size = extent.yMaximum() - extent.yMinimum()

    tile_factor = max_height_tile_size // settings.chunk_size * settings.sample_per_m
    real_tile_size_m = tile_factor*settings.chunk_size // settings.sample_per_m

    x_tiles_count = math.ceil(x_size / real_tile_size_m)
    y_tiles_count = math.ceil(y_size / real_tile_size_m)
    x = extent.xMinimum()
    y = extent.yMinimum()
    print(real_tile_size_m)
    for x_tile in range(x_tiles_count):
        for y_tile in range(y_tiles_count):
            left_top = proj_transform(inProj, outProj, x, y)
            right_bottom = proj_transform(
                inProj, outProj, x + real_tile_size_m, y + real_tile_size_m)
            print(left_top, right_bottom)
            __getTileHeight(left_top[0], left_top[1], right_bottom[0], right_bottom[1],
                                     "temp")

            image = open_image("temp.jpg")
            image = image.resize(
                (real_tile_size_m, real_tile_size_m), PIL.Image.Resampling.BICUBIC)
            height_chunk_size_m = real_tile_size_m // tile_factor
            for x_chunk in range(tile_factor):
                for y_chunk in range(tile_factor):
                    chunk_image = image
                    print(x_chunk*height_chunk_size_m,
                          real_tile_size_m, tile_factor)
                    chunk_image = chunk_image.crop(
                        [x_chunk*height_chunk_size_m, y_chunk*height_chunk_size_m, (x_chunk+1)*height_chunk_size_m, (y_chunk+1)*height_chunk_size_m])
                    chunk_image = chunk_image.resize(
                        [settings.chunk_size // 2, settings.chunk_size // 2])
                    chunk_image.save(os.path.join(settings.height_settings.heightPath,"{2}_{0}_{1}.jpg".format(
                        x_chunk + x_tile*tile_factor, y_chunk + y_tile*tile_factor, layer_name)))

            y += real_tile_size_m
        x += real_tile_size_m