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

# Bounding box for Netflix ad(s), adjust to screen size
bbox = {'top': 30, 'left': 1720, 'width': 200, 'height': 60}
root = tk.Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
ratios = width / 1920, height / 1080
bbox['top'] = int(bbox['top'] * ratios[1])
bbox['left'] = int(bbox['left'] * ratios[0])
bbox['width'] = int(bbox['width'] * ratios[0])
bbox['height'] = int(bbox['height'] * ratios[1])


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

        # Debugging
        """cv2.imshow('test', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()"""

        # Use tesseract to read text from image
        text = pytesseract.image_to_string(img, config='--psm 3')
        # If any digit is found, mute for that many seconds
        if any(i.isdigit() for i in text):
            if not muted:
                mute()
                try:
                    sleep(int(''.join(filter(str.isdigit, text))))
                except OverflowError:
                    continue
        # If 'ad' is found, mute
        elif 'ad' in text.lower():
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
