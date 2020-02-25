from ctypes import *
import sys

is_64bit_arch = sys.maxsize > 2**32 # здесь определяется разрядность архитектуры

# ниже я просто определили необходимые типы для удобства
LONG_PTR = c_longlong if is_64bit_arch else c_long
UINT_PTR = c_ulonglong if is_64bit_arch else c_uint
UINT = c_uint
HANDLE = c_void_p
WPARAM = UINT_PTR
LPARAM = LONG_PTR
LRESULT = LONG_PTR
HWND = HANDLE
LPCSTR = c_char_p
DWORD = c_ulong
WORD = c_ushort
SendMessage = windll.user32.SendMessageA
FindWindow = windll.user32.FindWindowA
MapVirtualKey = windll.user32.MapVirtualKeyA

# непосредственно функция, которая принимает виртуальный код клавиши
# https://msdn.microsoft.com/en-us/library/windows/desktop/dd375731(v=vs.85).aspx
def press_key(key_vk, window_title):
    c_window_title = LPCSTR(window_title.encode('utf-8'))

    WM_KEYUP = UINT(0x0101)
    WM_KEYDOWN = UINT(0x0100)
    wParam = WPARAM(key_vk)
    key_sc = MapVirtualKey(key_vk, 0)
    lParam = LPARAM(0x1 | (key_sc << 16))
    lParamDown = LPARAM(1 + (key_sc << 16) + (1 << 30))
    lParamUp = LPARAM(1 + (3 << 30) + (key_sc << 16))
    # находим хендл окна
    handle = FindWindow(LPCSTR(), c_window_title)
    # отправляем сообщение о нажатии клавиши
    SendMessage(handle, WM_KEYDOWN, wParam, lParamDown)
    # отправляем сообщение об отпускании клавиши
    return SendMessage(handle, WM_KEYUP, wParam, lParamUp)

# пример вызова функции. Код 0x20 это пробел. Как видите, я отправлял
# сообщение в плеер, и видео останавливалось и продолжалось :)
press_key(0x20, "Идфсл")