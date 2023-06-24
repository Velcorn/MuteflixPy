import cv2
import numpy as np
import pytesseract
import tkinter as tk
from tkinter import ttk
from mss import mss
from time import sleep
import threading

# Handle different OSes
from sys import platform

if platform == "win32":
    from pycaw.pycaw import AudioUtilities
    import pythoncom
elif platform == "darwin":
    import osascript
else:
    import subprocess

# Bounding boxes for Netflix and Twitch ads
bounding_boxes = {
    'netflix': {'top': 30, 'left': 1720, 'width': 200, 'height': 160},
    'twitch': {'top': 0, 'left': 0, 'width': 290, 'height': 200}
}

# Adjust bounding box based on screen resolution
root = tk.Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
ratios = width / 1920, height / 1080
for bbox in bounding_boxes.values():
    bbox['top'] = int(bbox['top'] * ratios[1])
    bbox['left'] = int(bbox['left'] * ratios[0])
    bbox['width'] = int(bbox['width'] * ratios[0])
    bbox['height'] = int(bbox['height'] * ratios[1])

muted = False  # Initial state
is_running = False  # Flag to control script execution
current_platform = 'netflix'  # Initial platform


def mute():
    global muted
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
    muted = True
    update_status_label()


def unmute():
    global muted
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
    muted = False
    update_status_label()


def update_status_label():
    if muted:
        status_label.config(text="Muted", fg="red")
    else:
        status_label.config(text="Unmuted", fg="green")


def toggle_mute():
    if muted:
        unmute()
    else:
        mute()


def toggle_platform():
    global current_platform
    if current_platform == 'netflix':
        current_platform = 'twitch'
    else:
        current_platform = 'netflix'
    toggle_button.config(text=current_platform.capitalize())


def toggle_script_execution():
    global is_running
    is_running = not is_running
    if is_running:
        start_stop_button.config(text="Stop")
        script_thread = threading.Thread(target=run_script_wrapper)
        script_thread.daemon = True
        script_thread.start()
    else:
        start_stop_button.config(text="Start")


# GUI setup
root.title("MuteflixPy")
root.geometry("300x160")  # Initial window size
root.resizable(True, True)  # Make window resizable

toggle_button = ttk.Button(root, text=current_platform.capitalize(), command=toggle_platform)
toggle_button.pack(pady=10)
toggle_button.config(text=current_platform.capitalize())

start_stop_button = ttk.Button(root, text="Start", command=toggle_script_execution)
start_stop_button.pack(pady=5)

status_label = tk.Label(root, text="Unmuted", fg="green")
status_label.pack()


# Main script loop wrapper
def run_script_wrapper():
    # Initialize the COM library for Windows
    if platform == "win32":
        pythoncom.CoInitialize()
    run_script()


# Main script loop
def run_script():
    while is_running:
        # Initialize screen capture
        sct = mss()
        # Take screenshot of the current platform's bounding box
        bbox = bounding_boxes[current_platform]
        img = np.array(sct.grab(bbox))
        # Binarize the image so only white text on black background remains
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # Use Tesseract to read text from image
        text = pytesseract.image_to_string(img, config='--psm 3')
        print(text)
        # Detects ads and mute/unmute accordingly
        ad_detected = 'catch' in text.lower() if current_platform == 'twitch' else \
            any(w in text.lower() for w in ['ad', '|'])
        if ad_detected:
            if not muted:
                mute()
                sleep(0.5)
            else:
                sleep(0.5)
        # Otherwise, unmute if muted
        elif muted:
            unmute()
            sleep(0.5)


root.mainloop()
