import time
from PIL import ImageOps, Image, ImageGrab
import os
import imagehash
from numpy import *
import cv2
import serial
from pynput import mouse
from matplotlib import pyplot as plt
#!/usr/bin/env python

"""Find the currently active window."""

import logging
import sys

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.DEBUG,
                    stream=sys.stdout)


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
    elif sys.platform in ['Mac', 'darwin', 'os2', 'os2emx']:
        # http://stackoverflow.com/a/373310/562769
        from AppKit import NSWorkspace
        active_window_name = (NSWorkspace.sharedWorkspace()
                              .activeApplication()['NSApplicationName'])
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

Mouse=mouse.Controller()


goodfishlist=os.listdir("loot/trash/")
goodfish=[]
for i in range(len(goodfishlist)):
    goodfish.append(str(imagehash.phash(Image.open("loot/trash/"+goodfishlist[i]))))

for i in range(len(goodfishlist)):
    for j in range(len(goodfish)):
        if goodfishlist[i]!= goodfishlist[j] and goodfish[i]==goodfish[j]:
            os.remove("loot/trash/"+goodfishlist[j])



while True:
    time.sleep(0.5)
    print(Mouse.position)


#400(299) 200(126) 100(56)