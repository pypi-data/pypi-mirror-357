import ctypes
from ctypes import wintypes
from .window import Window
from .button import Button
from . import core as C

__all__ = ["Window", "Button"]

wintypes.HICON = wintypes.HANDLE
wintypes.HCURSOR = wintypes.HANDLE
wintypes.HBRUSH = wintypes.HANDLE
wintypes.HDC = wintypes.HANDLE

if not hasattr(wintypes, "LRESULT"):
    wintypes.LRESULT = ctypes.c_ssize_t
    
class PAINTSTRUCT(ctypes.Structure):
    _fields_ = [
        ("hdc", wintypes.HDC), ("fErase", wintypes.BOOL), ("rcPaint", C.RECT),
        ("fRestore", wintypes.BOOL), ("fIncUpdate", wintypes.BOOL),
        ("rgbReserved", ctypes.c_byte * 32)
    ]
WNDPROCTYPE = ctypes.WINFUNCTYPE(
    wintypes.LRESULT, wintypes.HWND, wintypes.UINT,
    wintypes.WPARAM, wintypes.LPARAM)
