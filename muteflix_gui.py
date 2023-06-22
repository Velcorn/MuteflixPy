import numpy as np
import pytesseract
import tkinter as tk
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

# Bounding box for Netflix ad, adjust to screen size
bbox = {'top': 30, 'left': 1720, 'width': 200, 'height': 60}
root = tk.Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
ratios = width / 1920, height / 1080
bbox['top'] = int(bbox['top'] * ratios[1])
bbox['left'] = int(bbox['left'] * ratios[0])
bbox['width'] = int(bbox['width'] * ratios[0])
bbox['height'] = int(bbox['height'] * ratios[1])

muted = False  # Initial state
is_running = False  # Flag to control script execution


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
root.geometry("300x100")  # Initial window size
root.resizable(True, True)  # Make window resizable
start_stop_button = tk.Button(root, text="Start", command=toggle_script_execution)
start_stop_button.pack(pady=10)
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
        sct = mss()
        img = np.array(sct.grab(bbox))

        # Use tesseract to read text from image
        text = pytesseract.image_to_string(img, config='--psm 3')
        # If any digit is found, mute for that many seconds
        if any(i.isdigit() for i in text):
            if not muted:
                mute()
                sleep(int(''.join(filter(str.isdigit, text))))
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


root.mainloop()
