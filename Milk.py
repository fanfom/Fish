import logging
import time
from pynput import mouse
import serial
from numpy import *
import cv2
from PIL import ImageOps, Image, ImageGrab, ImageChops
from matplotlib import pyplot as plt


def get_active_window():
    """
    Get the currently active window.

    Returns
    -------
    string :
        Name of the currently active window.
    """
    import sys
    active_window_name = None
    if sys.platform in ['linux', 'linux2']:
        # Alternatives: http://unix.stackexchange.com/q/38867/4784
        try:
            import wnck
        except ImportError:
            logging.info("wnck not installed")
            wnck = None
        if wnck is not None:
            screen = wnck.screen_get_default()
            screen.force_update()
            window = screen.get_active_window()
            if window is not None:
                pid = window.get_pid()
                with open("/proc/{pid}/cmdline".format(pid=pid)) as f:
                    active_window_name = f.read()
        else:
            try:
                from gi.repository import Gtk, Wnck
                gi = "Installed"
            except ImportError:
                logging.info("gi.repository not installed")
                gi = None
            if gi is not None:
                Gtk.init([])  # necessary if not using a Gtk.main() loop
                screen = Wnck.Screen.get_default()
                screen.force_update()  # recommended per Wnck documentation
                active_window = screen.get_active_window()
                pid = active_window.get_pid()
                with open("/proc/{pid}/cmdline".format(pid=pid)) as f:
                    active_window_name = f.read()
    elif sys.platform in ['Windows', 'win32', 'cygwin']:
        # http://stackoverflow.com/a/608814/562769
        import win32gui
        window = win32gui.GetForegroundWindow()
        active_window_name = win32gui.GetWindowText(window)
    else:
        print("sys.platform={platform} is unknown. Please report."
              .format(platform=sys.platform))
        print(sys.version)
    return active_window_name


def get_screen(x1, y1, x2, y2):
    box = (x1 + 8, y1 + 30, x2 - 8, y2)
    screen = ImageGrab.grab(box)
    img = array(screen.getdata(), dtype=uint8).reshape((screen.size[1], screen.size[0], 3))
    return img


Mouse = mouse.Controller()
Arduino = serial.Serial('COM6', 9600)
time.sleep(1)
while True:
    if get_active_window()[:12] == "Black Desert":
        Arduino.write(("Beer{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}").encode())
        time.sleep(10)

        img = get_screen(0, 0, 1920, 1080)
        target = cv2.inRange(img, array([80, 50, 110], uint8), array([90, 65, 122], uint8))
        print(count_nonzero(target))
        if count_nonzero(target) > 0:
            print("r")
            Arduino.write("r".encode())
            time.sleep(0.5)
            print("Milk")
            Arduino.write("milk".encode())
        time.sleep(300)
    else:
        time.sleep(0.1)
        continue
