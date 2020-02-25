import logging
import random
import sys
import threading
import time
from pynput import mouse
import cv2
import pylab as pl
import serial
from PIL import ImageOps, Image, ImageGrab, ImageChops
from matplotlib import pyplot as plt
from numpy import *
import os
import imagehash

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result
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
def get_screen1(x1, y1, x2, y2):
    box = (x1 + 8, y1 + 30, x2 - 8, y2)
    screen = ImageGrab.grab(box)
    return screen
def phase2(Arduino=serial.Serial()):
    # Анализ букв
    out=""
    screen_phase2 = get_screen(700, 300, 1200, 450)
    countour_img = cv2.inRange(screen_phase2, array([53,53,58],uint8),array([53,53,58],uint8))
    contours, hierarchy = cv2.findContours(countour_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)



    charfish = []
    sizefish = []

    for i in range(len(contours)):
        if len(contours[i]) == 4:
            x, y, width, height = cv2.boundingRect(contours[i])
            y += 30
            height -= 32
            x += 2
            width -= 3
            if height < 0 or y < 0:
                continue
            roi = screen_phase2[y:y + height, x:x + width]

            for x in range(len(roi)):
                for y in range(len(roi[x])):
                        if (roi[x][y][0]<80)and(roi[x][y][1]<80)and(roi[x][y][2] < 80):
                            roi[x][y] = 0
                        else:
                            roi[x][y] = int(255)
            if int(count_nonzero(roi)) !=0:
                charfish.append(roi)
    if len(charfish) < 2:
        print("fall")
        return
    for i in range(len(charfish)):
        w = len(charfish[i])
        h = len(charfish[i][0])
        count = int(0)
        list_x = []
        list_y = []
        for x in range(w):
            for y in range(h):
                if (charfish[i][x][y][0] == 255):
                    count += 1
            if (count != 0):
                list_x.append(count)
            count = 0
        count = 0
        for y in range(h):
            for x in range(w):
                if (charfish[i][x][y][0] == 255):
                    count += 1
            if (count != 0):
                list_y.append(count)
                count = 0
        x1 = 0
        x2 = 0
        y1 = 0
        y2 = 0
        if len(list_x) % 2 != 0:
            list_x.pop(int(len(list_x) / 2))
        if len(list_y) % 2 != 0:
            list_y.pop(int(len(list_y) / 2))
        l = int(len(list_x) / 2)
        for i in range(l):
            x1 += list_x[i]
            x2 += list_x[len(list_x) - 1 - i]
        l = int(len(list_y) / 2)
        for i in range(l):
            y1 += list_y[i]
            y2 += list_y[len(list_y) - 1 - i]
        if abs(x1 - x2) > abs(y1 - y2):
            if x1 > x2:
                out = out + 's'
            else:
                out = out + 'w'
        else:
            if y1 > y2:
                out = out + 'd'
            else:
                out = out + 'a'
    time.sleep(1)
    Arduino.write(out[::-1].encode())
    print(out[::-1])
    time.sleep(6)
    getloot(Arduino)
    time.sleep(1)
def getloot (Arduino=serial.Serial()):
    screen_loot = get_screen(1400, 470, 1740, 630)
    loot=screen_loot
    ret, screen_loot = cv2.threshold(screen_loot, 60, 255, cv2.THRESH_BINARY)
    screen_loot = cv2.cvtColor(screen_loot, cv2.COLOR_BGR2GRAY)
    contours, hierarchy = cv2.findContours(screen_loot, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print("check loot")
    s = ""
    if (len(contours))!=12:
        print ("ALLERT")
        return
    f=0
    for i in range(len(contours)-1,0,-1):
        f+=1
        eq=False
        x, y, width, height = cv2.boundingRect(contours[i])
        roi = screen_loot[y:y + height, x:x + width]
        roiloot=loot[y:y + height, x:x + width]
        if(count_nonzero(roiloot>100)):
            t=imagehash.phash(Image.fromarray(roiloot,'RGB'))
            t1=Image.fromarray(roiloot,'RGB')
            for n in range(len(goodfish)):
                if t==goodfish[n]:
                    print("good")
                    Arduino.write("Ctrl".encode())
                    time.sleep(1)
                    s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(int(1380 + f * 50)) + ",530]"
                    print(s)
                    Arduino.write(s.encode())
                    time.sleep(1)
                    Arduino.write("Ctrl".encode())
                    eq=True
            for n in range(len(trashfish)):
                if t == trashfish[n]:
                    print("trash")
                    eq = True
                    break
            for n in range(len(mbfish)):
                if t == mbfish[n]:
                    print("mb")
                    eq = True
                    break
            if eq==False:
                print("hz",t)
                t1.save("loot/mb/"+str(random.random())+".jpg")
def nextrod (Arduino=serial.Serial()):
    Arduino.write("i".encode())
    time.sleep(1)
    inv=get_screen(1450,290,1900,760)
    inv_c = cv2.inRange(inv, array([240,180,55],uint8),array([250,190,62],uint8))
    inv_c += cv2.inRange(inv, array([62,135,200],uint8),array([70,145,210],uint8))
    inv_c += cv2.inRange(inv, array([40,45,55],uint8),array([50,60,65],uint8))
    inv_c += cv2.inRange(inv, array([125,160,60],uint8),array([135,170,70],uint8))
    contours, hierarchy = cv2.findContours(inv_c, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    n=1
    for i in range(len(contours)-1,0,-1):
        if len(contours[i]) == 8:
            x, y, width, height = cv2.boundingRect(contours[i])
            if (width<40)or(height<40):
                continuei
            roi = inv[y:y + height, x:x + width]
            inv_c = cv2.inRange(roi, array([240, 180, 55], uint8), array([250, 190, 62], uint8))
            if count_nonzero(inv_c):
                n += 1
                continue
            if imagehash.phash(Image.fromarray(roi))==rods[0]:
                if (n%8)!=0:
                    s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(
                        int(1420 + ((n % 8)) * 60)) + "," + str(350 + int((n) / 8) * 50) + "]"
                else:

                    s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(
                        int(1420 + 8 * 60)) + "," + str(350 + int((n) / 8) * 50) + "]"

                Arduino.write(s.encode())
                time.sleep(1)
                Arduino.write("i".encode())
                return
            n+=1


def hooking(Arduino=serial.Serial()):
    # Подсечка
    x=0
    while True:
        screen_phase1 = get_screen(990, 350, 1150, 395 )
        phase1 = cv2.inRange(screen_phase1, phase1_color, phase1_color_max)
        if (count_nonzero(phase1) > 300):
            print("подсек")
            Arduino.write("space".encode())
            break
        x+=1
        if x==20:
            break
Mouse=mouse.Controller()
fishing_color=array([220,220,220],uint8)
fishing_max = array([255,255,255],uint8)
countour_color=array([105,100,90],uint8)
countour_max = array([120,120,120],uint8)
space_color2=array([70,70,70],uint8)
space_color_max2 = array([100,100,100],uint8)
space_color=array([220,220,100],uint8)
space_color_max = array([255,255,255],uint8)
phase1_color=array([60,110,180],uint8)
phase1_color_max = array([180,255,255],uint8)
phase2_color=array([52,52,57],uint8)
phase2_color_max = array([54,54,59],uint8)

print("start")
time.sleep(2)
maplist=os.listdir("map/")
maphash=[]
imap=[]
for i in range(len(maplist)):
    imap.append(Image.open("map/"+maplist[i]))
    maphash.append(str(imagehash.phash(imap[i])))



screen_laki = get_screen(560, 190, 1170, 820)
x=14
y=5
height=46
width=48
#81416e7e6e2a3a3b

# 81416e7e6e2a3a3b 0
# c066261a3c6f7e39 32
# c0db7d4a6e092f32 22
# c0df16527b2b3b30 26
# c1262b3e7a166a3d 23
# c56e5e032e3a3f12 0
# d14b2e6a3a287f62 19
# d1b1e20f186f6734 0

plt.imshow(screen_laki,"gray")
plt.show()










