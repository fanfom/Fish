import logging
import random
import sys
import threading
import time
from pynput import mouse
import cv2
import serial
from PIL import ImageOps, Image, ImageGrab, ImageChops
from matplotlib import pyplot as plt
from numpy import *
import os
import imagehash
from timeit import default_timer as timer
import mss
import random as rd
import scipy
import scipy.misc
import scipy.cluster
from collections import Counter


def wait_arduino(arduino=serial.Serial):
    s = ""
    while s != "END":
        s += arduino.read().decode()
    time.sleep(0.1)


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


def phase2(Arduino=serial.Serial()):
    # Анализ букв
    out = ""
    charfish = []
    sizefish = []
    colorlist = []
    screen_phase2 = get_screen(700, 250, 1200, 500)
    t = cv2.inRange(screen_phase2, array([0, 0, 0], uint8), array([6, 6, 6], uint8))
    y_cord = 0
    for y in t:
        line = False
        lenght = 0
        x_cord = 0
        for pix in y:
            if pix == 255:
                if line:
                    lenght += 1
                    x_cord += 1
                else:
                    line = True
                    lenght += 1
                    x_cord += 1
            if pix == 0:
                if line:
                    break
                else:
                    x_cord += 1
            if lenght == 200:
                for r in range(9):
                    roi = screen_phase2[y_cord - 45:(y_cord - 45) + 17,
                          x_cord - 237 + 35 * r:(x_cord - 237) + 35 * r + 17]
                    if (roi[9, 9] - roi[9, 8])[0] != 0:
                        break
                    color1 = array([0, 0, 0], uint8)
                    color2 = array([0, 0, 0], uint8)
                    for n in range(3):
                        color1[n] = roi[9, 9][n] - 5
                        color2[n] = roi[9, 9][n] + 5
                        if color1[n] > roi[9, 9][n]:
                            color1[n] = roi[9, 9][n]
                        if color2[n] < roi[9, 9][n]:
                            color2[n] = roi[9, 9][n]
                    roi = cv2.inRange(roi, color1, color2)
                    charfish.append(roi)
                    plt.imshow(roi)
                    plt.show()
        if charfish:
            break

        y_cord += 1

    for i in range(len(charfish)):
        w = len(charfish[i])
        h = len(charfish[i][0])
        count = int(0)
        list_x = []
        list_y = []
        for y in range(w):
            for x in range(h):
                if charfish[i][x][y] == 255:
                    count += 1
            if count != 0:
                list_x.append(count)
            count = 0
        count = 0
        for x in range(h):
            for y in range(w):
                if charfish[i][x][y] == 255:
                    count += 1
            if count != 0:
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
        print(list_x)
        print(list_y)
        l = int(len(list_x) / 2)
        for i in range(l):
            x1 += list_x[i]
            x2 += list_x[len(list_x) - 1 - i]
        l = int(len(list_y) / 2)
        for i in range(l):
            y1 += list_y[i]
            y2 += list_y[len(list_y) - 1 - i]

        if len(list_x) > len(list_y):
            if y1 > y2:
                out = out + 's'
            else:
                out = out + 'w'
        else:
            if x1 > x2:
                out = out + 'd'
            else:
                out = out + 'a'
    Arduino.write(out.encode())
    print(out)
    time.sleep(5)
    getloot(Arduino)
    time.sleep(1)


def getloot(Arduino=serial.Serial()):
    screen_loot = get_screen(1525, 560, 1738, 738)
    loot = screen_loot
    ret, screen_loot = cv2.threshold(screen_loot, 60, 255, cv2.THRESH_BINARY)
    screen_loot = cv2.cvtColor(screen_loot, cv2.COLOR_BGR2GRAY)
    contours, hierarchy = cv2.findContours(screen_loot, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print("check loot")
    s = ""
    f = 0
    Arduino.write("Ctrl".encode())
    time.sleep(0.1)
    for i in range(len(contours) - 1, 0, -1):
        x, y, width, height = cv2.boundingRect(contours[i])
        if ((width > 50) or (height > 50)) or ((width < 40) or (height < 40)):
            continue
        f += 1
        eq = False
        gq = False

        roi = screen_loot[y:y + height, x:x + width]
        roiloot = loot[y:y + height, x:x + width]
        t = str(imagehash.phash(Image.fromarray(roiloot, 'RGB')))
        t1 = Image.fromarray(roiloot, 'RGB')
        if (count_nonzero(roiloot > 100)):
            gold = cv2.inRange(roiloot, array([230, 170, 50], uint8), array([255, 200, 100], uint8))
            if count_nonzero(gold) > 100:
                print("GOLD")
                if mode == "Gold" or mode == "Gar":
                    s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(
                        int(1500 + f * 50)) + ",615]"
                    Arduino.write(s.encode())
                    time.sleep(1)
                    continue

            for n in range(len(goodfish)):
                if t == goodfish[n]:
                    print("good")
                    s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(
                        int(1500 + f * 50)) + ",615]"
                    print(s)
                    Arduino.write(s.encode())
                    time.sleep(1)

                    eq = True
                    break
            for n in range(len(trashfish)):
                if t == trashfish[n]:
                    print("trash", trashfishlist[n])
                    if mode == "Gold":
                        sys.exit()
                    eq = True
                    break

            for n in range(len(mbfish)):
                if t == mbfish[n]:
                    print("mb")
                    s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(
                        int(1500 + f * 50)) + ",615]"
                    print(s)
                    Arduino.write(s.encode())
                    time.sleep(1)
                    eq = True
                    break

            if eq == False:
                print("hz", t)
                s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(
                    int(1500 + rd.randrange(-10, 10) + f * 50)) + "," + str(rd.randrange(-10, 10) + 615) + "]"
                Arduino.write(s.encode())
                time.sleep(1)
                t1.save("loot/mb/" + str(random.random()) + ".png")
    time.sleep(0.1)
    Arduino.write("Ctrl".encode())


def get_auk(Arduino=serial.Serial()):
    Arduino.write("Ctrl".encode())
    wait_arduino(Arduino)
    Arduino.write(("LClick{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + "330" + ",170]").encode())
    wait_arduino(Arduino)
    Arduino.write(("LClick{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + "850" + ",750]").encode())
    wait_arduino(Arduino)
    time.sleep(1)
    inv = get_screen(960, 280, 1450, 770)
    inv_t = cv2.inRange(inv, array([50, 50, 50], uint8), array([255, 255, 255], uint8))
    inv_t = inv_t + cv2.inRange(inv, array([30, 35, 40], uint8), array([40, 45, 50], uint8))
    contours, hierarchy = cv2.findContours(inv_t, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    n = 0
    for i in range(len(contours) - 1, 0, -1):
        x, y, width, height = cv2.boundingRect(contours[i])
        if ((width > 50) or (height > 50)) or ((width < 40) or (height < 40)):
            continue
        roi = inv[y:y + height - 20, x:x + width - 20]
        # print(str(imagehash.phash(Image.fromarray(roi))))
        # plt.imshow(roi)
        # plt.show()
        if str(imagehash.phash(Image.fromarray(roi))) == "bf4c92acda94a992":
            if (n % 8) != 0:
                s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(
                    int(985 + (n % 8 * 57))) + "," + str(350 + int((n) / 8) * 50) + "]"
                Arduino.write(s.encode())
                wait_arduino(Arduino)
                print(s, n)

            else:
                s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(
                    int(985 + (n % 8 * 60))) + "," + str(350 + int((n) / 8) * 50) + "]"
                Arduino.write(s.encode())
                wait_arduino(Arduino)
                print(s, n)

        n += 1
    Arduino.write("Esc".encode())
    wait_arduino(Arduino)


def nextrod(Arduino=serial.Serial()):
    # print("Beer{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}")
    # Arduino.write(("Beer{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}").encode())
    #
    # time.sleep(4.2)
    if altmode == "Char":
        Arduino.write("w".encode())
        wait_arduino(Arduino)
    Arduino.write("i".encode())
    time.sleep(0.5)
    s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(int(800)) + "," + str(100) + "]"
    Arduino.write(s.encode())
    time.sleep(0.5)
    fullstorage_img = get_screen(1440, 790, 1520, 850)
    fullstorage_img = cv2.inRange(fullstorage_img, array([230, 50, 50], uint8), array([250, 60, 60], uint8))
    if (count_nonzero(fullstorage_img) > 0):
        print("FULLSTORAGE")
        sys.exit()
    time.sleep(0.2)
    inv = get_screen(1120, 510, 1200, 610)
    inv_t = cv2.inRange(inv, array([50, 50, 50], uint8), array([255, 255, 255], uint8))
    contours, hierarchy = cv2.findContours(inv_t, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rodsalive = False
    for i in range(len(contours)):
        x, y, width, height = cv2.boundingRect(contours[i])
        if (width < 40) or (height < 40):
            continue
        roi = inv[y:y + height, x:x + width]

        for x in range(len(roi)):
            for y in range(len(roi[x])):
                if roi[x][y][0] < 90:
                    roi[x][y] = 0
                else:
                    roi[x][y] = 255
        if count_nonzero(roi) < 2000:
            rodsalive = True

    inv = get_screen(1350, 590, 1415, 675)
    inv_t = cv2.inRange(inv, array([50, 50, 50], uint8), array([255, 255, 255], uint8))
    contours, hierarchy = cv2.findContours(inv_t, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    chair_alive = False
    for i in range(len(contours)):
        x, y, width, height = cv2.boundingRect(contours[i])
        if (width < 40) or (height < 40):
            continue
        roi = inv[y:y + height, x:x + width]

        for x in range(len(roi)):
            for y in range(len(roi[x])):
                if roi[x][y][0] < 90:
                    roi[x][y] = 0
                else:
                    roi[x][y] = 255
        print(count_nonzero(roi))
        if count_nonzero(roi) < 2000:
            chair_alive = True
    print(chair_alive)
    if rodsalive and chair_alive:
        print("ok")
        time.sleep(0.1)
        Arduino.write("i".encode())
        return
    time.sleep(0.5)
    inv = get_screen(1450, 290, 1900, 760)
    inv_t = cv2.inRange(inv, array([30, 30, 30], uint8), array([255, 255, 255], uint8))
    contours, hierarchy = cv2.findContours(inv_t, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    n = 1
    rodchacnge = False
    chairchange = False
    if mode == "Rod":
        rodhash = rods[6]
    if mode == "Gold":
        rodhash = rods[1]
    if mode == "Start":
        rodhash = rods[3]
    if mode == "Gar":
        chair_hash = rods[5]
        rodhash = rods[0]
    else:
        chairchange = True
    for i in range(len(contours) - 1, 0, -1):
        if len(contours[i]) == 4:
            x, y, width, height = cv2.boundingRect(contours[i])
            if (width < 40) or (height < 40):
                continue
            roi = inv[y:y + height, x:x + width]
            inv_c = cv2.inRange(roi, array([240, 180, 55], uint8), array([250, 190, 62], uint8))
            if count_nonzero(inv_c) > 0:
                n += 1
                continue
            if imagehash.phash(Image.fromarray(roi)) == rodhash and rodsalive == False:
                if (n % 8) != 0:
                    s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(
                        int(1420 + (n % 8 * 57))) + "," + str(360 + int((n) / 8) * 50) + "]"
                else:

                    s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(
                        int(1420 + (n % 8 * 60))) + "," + str(360 + int((n) / 8) * 50) + "]"
                print(s, n)
                Arduino.write(s.encode())
                time.sleep(1)
                rodsalive = True
                continue
            if mode == "Gar" and imagehash.phash(Image.fromarray(roi)) == chair_hash and chair_alive == False:
                if (n % 8) != 0:
                    s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(
                        int(1420 + (n % 8 * 57))) + "," + str(360 + int((n) / 8) * 50) + "]"
                else:

                    s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(
                        int(1420 + (n % 8 * 60))) + "," + str(360 + int((n) / 8) * 50) + "]"
                print(s, n)
                Arduino.write(s.encode())
                time.sleep(1)
                chair_alive = True
                continue
            if chairchange and rodchacnge:
                Arduino.write("i".encode())
                return
            n += 1
    wait_arduino(Arduino)
    Arduino.write("i".encode())


def delete_(Arduino=serial.Serial(), n=-1):
    if n == -1:
        return
    time.sleep(1)
    if (n % 8) != 0:
        s = "Drag{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(
            int(1420 + (n % 8 * 57))) + "," + str(360 + int((n) / 8) * 50) + "]" + "<1860?850>"
    else:
        s = "Drag{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(
            int(1420 + (n % 8 * 60))) + "," + str(360 + int((n) / 8) * 50) + "]" + "<1860?850>"
    Arduino.write(s.encode())
    time.sleep(2)
    s = "LClick{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + "850,450]"
    print(s)
    Arduino.write(s.encode())
    wait_arduino(Arduino)


def delete_inv(Arduino=serial.Serial()):
    Arduino.write("i".encode())
    time.sleep(0.5)
    s = "Loot{" + str(Mouse.position[0]) + "|" + str(Mouse.position[1]) + "}[" + str(int(800)) + "," + str(100) + "]"
    Arduino.write(s.encode())
    wait_arduino(Arduino)
    inv = get_screen(1450, 290, 1900, 760)
    inv_t = cv2.inRange(inv, array([30, 30, 30], uint8), array([255, 255, 255], uint8))
    contours, hierarchy = cv2.findContours(inv_t, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    n = 1
    for i in range(len(contours) - 1, 0, -1):
        if len(contours[i]) == 4:
            x, y, width, height = cv2.boundingRect(contours[i])
            if (width < 40) or (height < 40):
                continue
            roi = copy(inv)[y:y + height, x:x + width]
            for x in range(len(roi)):
                for y in range(len(roi[x])):
                    if roi[x][y][0] < 20:
                        roi[x][y] = 0
                    else:
                        roi[x][y] = 255
            if count_nonzero(roi) > 5000:
                delete_(Arduino, n)
                return
                n -= 1
            n += 1
    Arduino.write("i".encode())


def hooking(Arduino=serial.Serial()):
    # Подсечка
    x = 0
    while True:
        time.sleep(0.1)
        screen_phase1 = array(grab.grab({"top": 405, "left": 1000, "width": 80, "height": 20}), uint8)
        screen_phase1 = cv2.cvtColor(screen_phase1, cv2.COLOR_RGB2BGR)
        ret, phase1 = cv2.threshold(screen_phase1, 60, 255, cv2.THRESH_BINARY)
        if (count_nonzero(phase1) > 2000):
            print("подсек")
            Arduino.write("space".encode())
            return
        x += 1
        if x == 20:
            return


def findobject(target):
    if count_nonzero(target) < 50:
        return (0, 0)
    for x in range(0, len(target), 4):
        for y in range(0, len(target[x]), 4):
            if target[x, y] == 255:
                start = (x, y)
                while (target[x, y] != 0) and x != len(target - 1) and y != len(target[x] - 1):
                    x += 5
                    y += 5
                end = (x, y)
                return (int((start[0] + end[0]) / 2), int((start[1] + end[1]) / 2))


Mouse = mouse.Controller()
fishing_color = array([220, 220, 220], uint8)
fishing_max = array([255, 255, 255], uint8)
countour_color = array([105, 100, 90], uint8)
countour_max = array([120, 120, 120], uint8)
space_color2 = array([70, 70, 70], uint8)
space_color_max2 = array([100, 100, 100], uint8)
space_color = array([220, 220, 100], uint8)
space_color_max = array([255, 255, 255], uint8)
phase1_color = array([60, 110, 180], uint8)
phase1_color_max = array([180, 255, 255], uint8)
phase2_color = array([52, 52, 57], uint8)
phase2_color_max = array([54, 54, 59], uint8)

print("start")

Arduino = serial.Serial('COM3', 9400)
time.sleep(2)
print(123)
goodfishlist = os.listdir("loot/good/")
goodfish = []
for i in range(len(goodfishlist)):
    goodfish.append(str(imagehash.phash(Image.open("loot/good/" + goodfishlist[i]))))
trashfishlist = os.listdir("loot/trash")
trashfish = []
for i in range(len(trashfishlist)):
    trashfish.append(str(imagehash.phash(Image.open("loot/trash/" + trashfishlist[i]))))
mbfishlist = os.listdir("loot/mb")
mbfish = []
for i in range(len(mbfishlist)):
    mbfish.append(str(imagehash.phash(Image.open("loot/mb/" + mbfishlist[i]))))
rodlist = os.listdir("rod")
rods = []
for i in rodlist:
    rods.append(imagehash.phash(Image.open("rod/" + i)))

time.sleep(0.1)
mode = "Rod"
altmode = ""
# get_auk(Arduino)
while True:
    print(Mouse.position)