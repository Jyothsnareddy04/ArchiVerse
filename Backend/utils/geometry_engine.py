import cv2
import numpy as np


def extract_room_rectangles(mask):

    rects = []

    for cls in np.unique(mask):

        if cls == 0:
            continue

        binary = (mask == cls).astype(np.uint8)

        contours,_ = cv2.findContours(
            binary,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        for c in contours:

            if cv2.contourArea(c) < 200:
                continue

            x,y,w,h = cv2.boundingRect(c)

            rects.append((x,y,w,h,cls))

    return rects