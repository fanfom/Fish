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
from timeit import default_timer as timer
import mss
import random as rd



def wait_arduino(arduino=serial.Serial):
    s=""
    while s!="END":
        s+=arduino.read().decode()
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
    Arduino.write(out[::-1].encode())
    print(out[::-1])
    time.sleep(5)
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
    f=0
    Arduino.write("Ctrl".encode())
    time.sleep(0.1)
    for i in range(len(contours)-1,0,-1):
        x, y, width, height = cv2.boundingRect(contours[i])
        if ((width > 50) or (height > 50)) or ((width < 40) or (height < 40)):
            continue
        f+=1
        eq=False
        gq=False


        roi = screen_loot[y:y + height, x:x + width]
        roiloot=loot[y:y + height, x:x + width]
        t = str(imagehash.phash(Image.fromarray(roiloot, 'RGB')))
        t1 = Image.fromarray(roiloot, 'RGB')
        if(count_nonzero(roiloot>100)):
            gold= cv2.inRange   (roiloot, array([230,170,50],uint8), array([255,200,100],uint8))
            if count_nonzero(gold)>100:
                print("GOLD")
                s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(
                    int(1380 + f * 50)) + ",530]"
                Arduino.write(s.encode())
                time.sleep(1)

                continue


            for n in range(len(goodfish)):
                if t==goodfish[n]:
                    print("good")
                    s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(
                        int(1380 + f * 50)) + ",530]"
                    print(s)
                    Arduino.write(s.encode())
                    time.sleep(1)

                    eq=True
                    break
            for n in range(len(trashfish)):
                if t == trashfish[n]:
                    print("trash")
                    eq = True
                    break

            for n in range(len(mbfish)):
                if t == mbfish[n]:
                    print("mb")
                    s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(
                        int(1380 + f * 50)) + ",530]"
                    print(s)
                    Arduino.write(s.encode())
                    time.sleep(1)
                    Arduino.write("Ctrl".encode())
                    time.sleep(0.1)
                    eq = True
                    break

            if eq==False:
                print("hz",t)
                s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(
                    int(1380+rd.randrange(-10,10) + f * 50)) + ","+str(rd.randrange(-10,10) + 530)+"]"
                Arduino.write(s.encode())
                time.sleep(1)
                t1.save("loot/mb/"+str(random.random())+".png")
    time.sleep(0.1)
    Arduino.write("Ctrl".encode())
def nextrod (Arduino=serial.Serial()):
    #print("Beer{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}")
    #Arduino.write(("Beer{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}").encode())

    time.sleep(4.2)
    Arduino.write("i".encode())
    time.sleep(0.5)
    if(Mouse.position[0]<900 or Mouse.position[0]>1200)and(Mouse.position[1]>600 or Mouse.position[1]<400):
        s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(
            int(800)) + "," + str(100) + "]"
        Arduino.write(s.encode())
        time.sleep(0.5)
    fullstorage_img = get_screen(1440, 790, 1520, 850)
    fullstorage_img = cv2.inRange(fullstorage_img,array([230,50,50],uint8),array([250,60,60],uint8))

    if (count_nonzero(fullstorage_img)>0):
        print("FULLSTORAGE")
        sys.exit()
    time.sleep(0.2)
    inv = get_screen(1120, 510, 1200, 610)
    inv_t = cv2.inRange(inv, array([50,50,50],uint8),array([255,255,255],uint8))
    contours, hierarchy = cv2.findContours(inv_t, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rodsalive=False
    for i in range(len(contours)):
            x, y, width, height = cv2.boundingRect(contours[i])
            if (width<40)or(height<40):
                continue
            roi = inv[y:y + height, x:x + width]

            for x in range(len (roi)):
                for y in range(len(roi[x])):
                    if roi[x][y][0]<90:
                        roi[x][y]=0
                    else:
                        roi[x][y]=255
            if count_nonzero(roi)<2000:
                rodsalive=True
    if rodsalive==True:
        print("rod")
        time.sleep(0.1)
        Arduino.write("i".encode())
        return
    time.sleep(0.5)
    inv=get_screen(1450,290,1900,760)
    inv_t = cv2.inRange(inv, array([30,30,30],uint8),array([255,255,255],uint8))
    contours, hierarchy = cv2.findContours(inv_t, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    n=1
    if mode == "Rod":
        rodhash = rods[2]
    if mode == "Gold":
        rodhash = rods[1]
    if mode == "Start":
        rodhash = rods[3]
    if mode=="Gar":
        rodhash = rods[0]
    for i in range(len(contours)-1,0,-1):
        if len(contours[i]) == 4:
            x, y, width, height = cv2.boundingRect(contours[i])
            if (width<40)or(height<40):
                 continue
            roi = inv[y:y + height, x:x + width]
            inv_c = cv2.inRange(roi, array([240, 180, 55], uint8), array([250, 190, 62], uint8))
            if count_nonzero(inv_c)>0:
                n += 1
                continue
            print(imagehash.phash(Image.fromarray(roi)),rodhash,imagehash.phash(Image.fromarray(roi))==rodhash)
            if imagehash.phash(Image.fromarray(roi))==rodhash:
                if (n%8)!=0:
                    s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(
                        int(1420 + (n % 8 * 57))) + "," + str(360 + int((n) / 8) * 50) + "]"
                else:

                    s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(
                        int(1420 + (n % 8 * 60))) + "," + str(360 + int((n) / 8) * 50) + "]"
                print(s, n)
                Arduino.write(s.encode())
                time.sleep(1)
                Arduino.write("i".encode())
                return


            n+=1
def hooking(Arduino=serial.Serial()):
    # Подсечка
    x=0
    while True:
        time.sleep(0.1)
        screen_phase1 = get_screen(1000, 345, 1155, 395)
        phase1 = cv2.inRange(screen_phase1, phase1_color, phase1_color_max)
        if (count_nonzero(phase1) > 300):
            print("подсек")
            Arduino.write("space".encode())
            break
        x+=1
        if x==5:
            break
def findobject(target):

    if count_nonzero(target)<50:
        return (0,0)
    for x in range(0,len(target),4):
        for y in range(0,len(target[x]),4):

            if target[x,y] == 255:
                start = (x, y)
                while (target[x, y] != 0) and x!=len(target-1) and y!=len(target[x]-1):
                    x += 4
                    y += 4
                end = (x, y)
                return (int((start[0]+end[0])/2),int((start[1]+end[1])/2))

goodfishlist=os.listdir("loot/good/")
print(goodfishlist)
goodfish=[]
for i in goodfishlist:
    goodfish.append(str(imagehash.phash(Image.open("loot/good/"+i))))
a=0
for hash in goodfish:
    for hash2 in goodfish:
        if hash==hash2:
            os.remove("loot/good/"+goodfishlist[a])
        a+=1