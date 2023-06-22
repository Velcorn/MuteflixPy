import cv2  # for debugging purposes
import numpy as np
import pytesseract
from mss import mss
from time import sleep

# Handle different OSes
from sys import platform
if platform == "win32":
    from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
elif platform == "darwin":
    import osascript
else:
    raise Exception("Unsupported OS")

# Bounding box for Netflix ad
# TODO: Make this dynamic based on screen size
bounding_box = {'top': 0, 'left': 1270, 'width': 140, 'height': 100}

# Main loop
sct = mss()
mute = False
while True:
    img = np.array(sct.grab(bounding_box))
    text = pytesseract.image_to_string(img, config='--psm 3')
    # If the text contains 'ad' or a number, mute the system
    if 'ad' in text.lower() or any(i.isdigit() for i in text):
        if not mute:
            print("Muting")
            mute = True
            if platform == "win32":
                sessions = AudioUtilities.GetAllSessions()
                for session in sessions:
                    volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                    volume.SetMute(1, None)
            else:
                osascript.osascript("set volume output muted TRUE")
        else:
            sleep(0.5)
    else:
        if mute:
            print("Unmuting")
            mute = False
            if platform == "win32":
                sessions = AudioUtilities.GetAllSessions()
                for session in sessions:
                    volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                    volume.SetMute(0, None)
            else:
                osascript.osascript("set volume output muted FALSE")
        else:
            sleep(0.5)
