import cv2
import numpy as np


COLORS = [
(0,0,0),
(255,0,0),
(0,255,0),
(0,0,255),
(255,255,0),
(255,0,255)
]


def colorize(layout):

    h,w = layout.shape

    img = np.zeros((h,w,3),dtype=np.uint8)

    for i,c in enumerate(COLORS):

        img[layout==i] = c

    return img