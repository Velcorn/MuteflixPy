import cv2  # for debugging purposes
import numpy as np
import pytesseract
import tkinter as tk
from mss import mss
from time import sleep

# Handle different OSes
from sys import platform
if platform == "win32":
    from pycaw.pycaw import AudioUtilities
elif platform == "darwin":
    import osascript
else:
    import subprocess

# Bounding box
bbox = {'top': 30, 'left': 1720, 'width': 200, 'height': 160}


def mute():
    if platform == "win32":
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and any(s in session.Process.name() for s in ['firefox', 'chrome']):
                volume = session.SimpleAudioVolume
                volume.SetMute(1, None)
        print("Muted")
    elif platform == "darwin":
        osascript.osascript("set volume output muted TRUE")
    else:
        subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "mute"])
    return True


def unmute():
    if platform == "win32":
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and any(s in session.Process.name() for s in ['firefox', 'chrome']):
                volume = session.SimpleAudioVolume
                volume.SetMute(0, None)
    elif platform == "darwin":
        osascript.osascript("set volume output muted FALSE")
    else:
        subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "unmute"])
    return False


if __name__ == "__main__":
    sct = mss()
    muted = False
    while True:
        img = np.array(sct.grab(bbox))

        # Binarize the image so only white text on black background remains
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # Debugging
        cv2.imshow('test', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # Use tesseract to read text from image
        text = pytesseract.image_to_string(img)
        print(text)
        # If 'ad' or any digit is found, mute
        if 'ad' in text.lower() or any(i.isdigit() for i in text):
            if not muted:
                mute()
                sleep(0.5)
            else:
                sleep(0.5)
        # Otherwise, unmute if muted
        else:
            if muted:
                unmute()
                sleep(0.5)
            else:
                sleep(0.5)
