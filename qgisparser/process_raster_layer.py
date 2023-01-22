import qgis.core as core
import numpy as np
import gc
from PIL.Image import fromarray
from multiprocessing import Process
from .get_height import *
from .utils.thread_provider import ThreadProvider
from .get_height import process_layer_height
from .utils.settings import Settings
import os.path

class Chunker:
    buffer: np.array
    chunk_size: int
    def __init__(self, chunk_size: int) -> None:
        self.chunk_size = chunk_size

        self.clear()

    def clear(self):
        self.buffer = np.zeros((self.chunk_size, self.chunk_size, 3), dtype=np.uint8)
        gc.collect()

    def set(self, x: int, y: int, channel: int, value: float | int):
        self.buffer[x][y][channel] = int(value)

    def save(self, name: str):
        if (np.sum(self.buffer) > 2*self.chunk_size):
            img = fromarray(self.buffer)
            img.save(name + ".png")

def createImage(layer: core.QgsRasterLayer, chunk_x: int, chunk_y: int, settings: Settings):
    extent: core.QgsRectangle = layer.extent()
    layer.triggerRepaint()
    dataProvider = layer.dataProvider()
    x_min = int(extent.xMinimum())
    y_min = int(extent.yMinimum())
    chunker = Chunker(settings.chunk_size)
    print(extent.xMinimum(), extent.xMaximum(),
          (chunk_x*settings.chunk_size)/settings.sample_per_m + x_min)
    for x in range(settings.chunk_size):
        for y in range(settings.chunk_size):
            current_x = (chunk_x*settings.chunk_size + x)/settings.sample_per_m + x_min
            current_y = (chunk_y*settings.chunk_size + y)/settings.sample_per_m + y_min
            for ch in range(1, 4):
                val, res = dataProvider.sample(core.QgsPointXY(
                    current_x, current_y), ch)
                chunker.set(
                    x,
                    y,
                    ch-1,
                    val if res else 0
                )
    chunker.save(
        os.path.join(settings.images_path,
        "{2}_{0}_{1}".format(chunk_x, chunk_y, layer.name())))

def multiband_layer_image(layer: core.QgsRasterLayer, settings: Settings):
    extent: core.QgsRectangle = layer.extent()
    layer.triggerRepaint(deferredUpdate=False)
    x_size = (int(extent.xMaximum())-int(extent.xMinimum()))*settings.sample_per_m
    x_chunks = x_size // settings.chunk_size
    y_size = (int(extent.yMaximum())-int(extent.yMinimum()))*settings.sample_per_m
    y_chunks = y_size // settings.chunk_size
    current_chunk = -1
    all_chunks = x_chunks * y_chunks
    thread_provider = ThreadProvider()

    height_scrabber = Process(
        target=process_layer_height, args=[layer.clone(), settings])
    height_scrabber.start()
    for x_i in range(x_chunks):
        for y_i in range(y_chunks):
            # os.system("clear")
            print("{0}% {1} of {2}".format((current_chunk*100) //
                  all_chunks, current_chunk, all_chunks))
            thread = Process(target=createImage, args=(
                layer.clone(), x_i, y_i, settings))
            thread_provider.add_thread(thread)
            thread.start()
            thread_provider.wait()
            current_chunk += 1
    height_scrabber.join()