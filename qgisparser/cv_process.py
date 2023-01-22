import cv2
import shelve
import numpy
import math
import os

sh = shelve.open("save")
map = numpy.array(sh.get("img"), dtype=numpy.uint8)
map = cv2.cvtColor(map, cv2.COLOR_RGB2BGR)
cv2.imwrite("save.png", map)

chunk_size = 256
y_map_size = len(map)
x_map_size = len(map[0])

y_chunks = math.ceil(y_map_size/chunk_size)
x_chunks = math.ceil(x_map_size/chunk_size)

print(x_chunks, y_chunks)

def check_crop(crop: list[list[list[float]]])->bool:
    if(len(crop)):
        passed = False
        for column in crop:
            for px in column:
                if(px[0] != 0):
                    passed = True
                    break
        return passed
    return False

from random import random


path_to_train = "./images/train/"
path_to_validate = "./images/validate/"
for x_ch in range(0, x_chunks):
    for y_ch in range(0, y_chunks):
        x = x_ch*chunk_size
        y = y_ch*chunk_size
        crop = map[x:x+chunk_size, y:y+chunk_size]
        if(check_crop(crop)):
            path = path_to_validate if random() < 0.2 else path_to_train
            cv2.imwrite("{0}{1}_{2}.png".format(os.path.join(path, "./HR/"), x_ch, y_ch), crop)
            crop = cv2.resize(crop, (chunk_size//4, chunk_size//4))
            cv2.imwrite("{0}{1}_{2}.png".format(os.path.join(path, "./LR/"), x_ch, y_ch), crop)