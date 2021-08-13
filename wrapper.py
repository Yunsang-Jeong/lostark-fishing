import ctypes
from ctypes import wintypes
import struct

class BITMAPFILEHEADER(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("bfType", wintypes.WORD),
        ("bfSize", wintypes.DWORD),
        ("bfReserved1", wintypes.WORD),
        ("bfReserved2", wintypes.WORD),
        ("bfOffBits", wintypes.DWORD)
    ]

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD)
    ]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ("bmiHeader", BITMAPINFOHEADER)
    ]


class BITMAP(ctypes.Structure):
    #_pack_ = 1
    _fields_ = [
        ("bmType", wintypes.LONG), # The bitmap type. This member must be zero.
        ("bmWidth", wintypes.LONG), # The width, in pixels, of the bitmap. The width must be greater than zero.
        ("bmHeight", wintypes.LONG), # The height, in pixels, of the bitmap. The height must be greater than zero.
        ("bmWidthBytes", wintypes.LONG), # The number of bytes in each scan line.
        ("bmPlanes", wintypes.WORD), # The count of color planes.
        ("bmBitsPixel", wintypes.WORD), # The number of bits required to indicate the color of a pixel.
        ("bmBits", ctypes.c_void_p) # A pointer to the location of the bit values for the bitmap.
    ]

class APIWrapper():
    def __init__(self, process_name):
        self.hwnd = 0
        self.hwndDC = 0
        self.user32 = ctypes.windll.user32
        self.gdi32 = ctypes.windll.gdi32
        self.dwmapi = ctypes.windll.dwmapi
        self.process_name = process_name
        self.real_process_name = process_name
        self.DIB_RGB_COLORS = 0
        self.BI_RGB = 0
        self.PW_CLIENTONLY = 0

        self.user32.GetClientRect.argtypes = [wintypes.HWND, wintypes.LPRECT]
        self.user32.GetClientRect.restype = wintypes.BOOL

        self.user32.GetCursorPos.argtypes = [wintypes.LPPOINT]
        self.user32.GetCursorPos.restype = wintypes.BOOL

        self.user32.GetWindowDC.argtypes = [wintypes.HWND]
        self.user32.GetWindowDC.restypes = wintypes.HDC

        self.gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
        self.gdi32.CreateCompatibleDC.restypes = wintypes.HDC

        self.gdi32.CreateCompatibleBitmap.argtypes = [wintypes.HDC, wintypes.INT, wintypes.INT]
        self.gdi32.CreateCompatibleBitmap.restypes = wintypes.HBITMAP

        self.gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
        self.gdi32.SelectObject.restypes = wintypes.HGDIOBJ

        self.user32.PrintWindow.argtypes = [wintypes.HDC, wintypes.HDC, wintypes.UINT]
        self.user32.PrintWindow.restypes = wintypes.BOOL

        self.gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
        self.gdi32.DeleteObject.restypes = wintypes.BOOL

        self.gdi32.GetDIBits.argtypes = [wintypes.HDC, wintypes.HBITMAP, wintypes.UINT, wintypes.UINT, ctypes.c_void_p, ctypes.POINTER(BITMAPINFO), wintypes.UINT]
        self.gdi32.GetDIBits.restypes = wintypes.INT

        self.user32.IsWindowVisible.argtypes = [wintypes.HWND]
        self.user32.IsWindowVisible.restypes = wintypes.BOOL

        self.user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
        self.user32.GetWindowTextLengthW.restypes = wintypes.INT

        self.user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, wintypes.LONG]
        self.user32.GetWindowTextW.restypes = wintypes.INT

        self.EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        self.user32.EnumWindows.argtypes = [self.EnumWindowsProc, wintypes.LPARAM]
        self.user32.EnumWindows.restypes = wintypes.BOOL

        self.user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
        self.user32.FindWindowW.restype = wintypes.HWND

        self.gdi32.GetPixel.argtypes = [wintypes.HWND, wintypes.INT, wintypes.INT]
        self.gdi32.GetPixel.restype = wintypes.COLORREF

        self.gdi32.GetObjectW.argtypes = [wintypes.HDC, wintypes.INT, wintypes.LPVOID]
        self.gdi32.GetObjectW.restype = wintypes.INT

        self.user32.SetCapture.argtypes = [wintypes.HWND]
        self.user32.SetCapture.restype = wintypes.HWND

        self.user32.ReleaseCapture.argtypes = []
        self.user32.ReleaseCapture.restype = wintypes.BOOL


    def __del__(self):
        if self.hwndDC != 0:
            self.gdi32.DeleteObject(self.hwndDC)

    def EnumWindowsProc_callback(self, hwnd, lParam):
        if self.user32.IsWindowVisible(hwnd):
            length = self.user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            self.user32.GetWindowTextW(hwnd, buff, length + 1)
            if self.process_name in buff.value:
                self.real_process_name = buff.value
                print('[*] Success to find process : {}'.format(buff.value))
                return False
        return True

    def getWindowHandle(self):
        self.user32.EnumWindows(self.EnumWindowsProc(self.EnumWindowsProc_callback), 0)
        self.hwnd = self.user32.FindWindowW(None, self.real_process_name)

    def getWindowHandleDC(self):
        self.hwndDC = self.user32.GetWindowDC(self.hwnd)

    def findSpecificPointRGB(self, x, y):
        if self.hwndDC == 0:
            print('[-] You must get windowDC handle.')
            return False
        else:
            pixel = self.gdi32.GetPixel(self.hwndDC, x, y)
            return (pixel&0xFF, pixel>>8&0xFF, pixel>>16&0xff)

    def getMouseCursor(self, obj):
        self.user32.GetCursorPos(obj)

    def setMouseCursor(self, xpos, ypos):
        self.user32.SetCursorPos(ctypes.c_int(xpos), ctypes.c_int(ypos))

    # https://stackoverflow.com/questions/24439949/winapi-getdibits-access-violation
    def screenshot(self):
        def roundUP(round, value):
            temp = round
            while round < value:
                round += temp
            return round

        rect = ctypes.wintypes.RECT()
        self.user32.GetClientRect(self.hwnd, ctypes.byref(rect))
        left, right, top, bottom = rect.left, rect.right, rect.top, rect.bottom
        width, height = right - left, bottom - top

        saveDC = self.gdi32.CreateCompatibleDC(self.hwndDC)
        bmpDC = self.gdi32.CreateCompatibleBitmap(self.hwndDC, width, height)
        self.gdi32.SelectObject(saveDC, bmpDC)
        self.user32.PrintWindow(self.hwnd, saveDC, self.PW_CLIENTONLY)

        objBITMAP = BITMAP()
        self.gdi32.GetObjectW(bmpDC, ctypes.sizeof(BITMAP), ctypes.byref(objBITMAP))
        bitmapDataSize = objBITMAP.bmWidth * objBITMAP.bmHeight * int(objBITMAP.bmBitsPixel/8)
        bitmapData = ctypes.create_string_buffer(bitmapDataSize)

        objBITMAPINFO = BITMAPINFO()
        bitmapInfoHeaderSize = ctypes.sizeof(BITMAPINFO)
        objBITMAPINFO.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        objBITMAPINFO.bmiHeader.biWidth = objBITMAP.bmWidth
        objBITMAPINFO.bmiHeader.biHeight = -objBITMAP.bmHeight
        objBITMAPINFO.bmiHeader.biPlanes = 1  # Always 1
        objBITMAPINFO.bmiHeader.biBitCount = objBITMAP.bmBitsPixel
        objBITMAPINFO.bmiHeader.biCompression = self.BI_RGB

        bitmapInfoHeader = ctypes.create_string_buffer(bitmapInfoHeaderSize)
        ctypes.memmove(bitmapInfoHeader, ctypes.addressof(objBITMAPINFO), bitmapInfoHeaderSize)

        objBITMAPFILEHEADER = BITMAPFILEHEADER()
        bitmapFileHeaderSize = ctypes.sizeof(BITMAPFILEHEADER)
        objBITMAPFILEHEADER.bfType = ctypes.wintypes.WORD(0x4D42)
        objBITMAPFILEHEADER.bfSize = ctypes.wintypes.DWORD(bitmapFileHeaderSize + bitmapInfoHeaderSize + bitmapDataSize)
        objBITMAPFILEHEADER.bfReserved1 = ctypes.wintypes.WORD(0x0000)
        objBITMAPFILEHEADER.bfReserved2 = ctypes.wintypes.WORD(0x0000)
        objBITMAPFILEHEADER.bfOffBits = ctypes.wintypes.DWORD(bitmapFileHeaderSize + bitmapInfoHeaderSize)

        bitmapFileHeader = ctypes.create_string_buffer(bitmapFileHeaderSize)
        ctypes.memmove(bitmapFileHeader, ctypes.addressof(objBITMAPFILEHEADER), bitmapFileHeaderSize)

        ctypes.windll.gdi32.GetDIBits(
            saveDC, # A handle to the device context.
            bmpDC, # A handle to the bitmap. This must be a compatible bitmap (DDB).
            0, # The first scan line to retrieve.
            objBITMAP.bmHeight, # The number of scan lines to retrieve.
            ctypes.byref(bitmapData), # A pointer to a buffer to receive the bitmap data.
            ctypes.byref(objBITMAPINFO), # A pointer to a BITMAPINFO structure that specifies the desired format for the DIB data.
            self.DIB_RGB_COLORS # The format of the bmiColors member of the BITMAPINFO structure
        )
        if saveDC:  self.gdi32.DeleteObject(saveDC)
        if bmpDC:   self.gdi32.DeleteObject(bmpDC)
        return bitmapFileHeader, bitmapInfoHeader, bitmapData
