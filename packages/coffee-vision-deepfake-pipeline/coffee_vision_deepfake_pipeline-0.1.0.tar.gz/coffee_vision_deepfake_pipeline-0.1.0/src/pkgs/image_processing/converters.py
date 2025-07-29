import cv2
import numpy as np

def image_bytes_to_rgb(img_bytes):
    np_arr = np.frombuffer(img_bytes, np.uint8)
    bgr_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    rgb_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
    return rgb_img
