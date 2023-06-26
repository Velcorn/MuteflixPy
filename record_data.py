import cv2
import numpy as np
import tkinter as tk
from mss import mss
from time import sleep

# Bounding box
bbox = {'top': 30, 'left': 1720, 'width': 200, 'height': 160}
# Adjust bounding box based on screen resolution
root = tk.Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
ratios = width / 1920, height / 1080
bbox['top'] = int(bbox['top'] * ratios[1])
bbox['left'] = int(bbox['left'] * ratios[0])
bbox['width'] = int(bbox['width'] * ratios[0])
bbox['height'] = int(bbox['height'] * ratios[1])

sct = mss()
counter = 0
while True:
    if counter == 10000:
        break
    # Grab the image
    img = np.array(sct.grab(bbox))
    # Save the image
    cv2.imwrite(f'images/{counter.zfill(5)}.jpg', img)
    counter += 1
    # Sleep 1 second
    sleep(1)
