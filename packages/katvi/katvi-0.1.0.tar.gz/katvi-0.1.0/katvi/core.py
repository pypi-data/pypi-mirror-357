import ctypes
from ctypes import wintypes

# ----------------- CORE VARIABLES ------------------------
user32 = ctypes.WinDLL("user32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

# -------------- VARIABLES -------------------------------
BN_CLICKED = 0
BS_DEFPUSHBUTTON = 0x00000001
WS_CHILD = 0x40000000
WS_VISIBLE = 0x10000000
SWP_NOZORDER = 0x0004
WM_PAINT = 0x000F
WM_COMMAND = 0x0111
WM_DESTROY = 0x0002
CS_HREDRAW = 0x0002
CS_VREDRAW = 0x0001
WS_OVERLAPPEDWINDOW = 0x00CF0000
SW_SHOW = 5
WM_SETICON = 0x0080
ICON_SMALL = 0
ICON_BIG = 1
IMAGE_ICON = 1
LR_LOADFROMFILE = 0x00000010
LR_DEFAULTSIZE = 0x00000040
LF_FACESIZE = 32
WM_SETFONT = 0x0030
WM_GETFONT = 0x0031
BS_OWNERDRAW = 0x0000000B
WM_DRAWITEM = 0x002B
ODS_SELECTED = 0x0001
TRANSPARENT = 1
BLACK_BRUSH = 4


#0x00000000 -- BLACK
#0x00FFFFFF -- WHITE
#0x00707070 -- GRAY


gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
gdi32.SelectObject.restype = wintypes.HGDIOBJ
gdi32.RoundRect.restype = wintypes.BOOL
gdi32.CreatePen.argtypes = [ctypes.c_int, ctypes.c_int, wintypes.COLORREF]
gdi32.CreatePen.restype = wintypes.HPEN
gdi32.GetTextExtentPoint32W.argtypes = [wintypes.HDC, wintypes.LPCWSTR, ctypes.c_int, ctypes.POINTER(ctypes.c_long)]
gdi32.GetTextExtentPoint32W.restype = wintypes.BOOL
gdi32.TextOutW.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int, wintypes.LPCWSTR, ctypes.c_int]
gdi32.TextOutW.restype = ctypes.c_bool
gdi32.SetTextColor.argtypes = [wintypes.HDC, wintypes.COLORREF]
gdi32.SetTextColor.restype = wintypes.COLORREF
user32.FillRect.argtypes = [wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.HBRUSH]
user32.FillRect.restype = ctypes.c_int
user32.FrameRect.argtypes = [wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.HBRUSH]
user32.FrameRect.restype = ctypes.c_int
gdi32.SetBkMode.argtypes = [wintypes.HDC, ctypes.c_int]
gdi32.SetBkMode.restype = ctypes.c_int
SetProcessDpiAwareness = ctypes.windll.shcore.SetProcessDpiAwareness

gdi32.RoundRect.argtypes = [
    wintypes.HDC,
    ctypes.c_int, ctypes.c_int,
    ctypes.c_int, ctypes.c_int,
    ctypes.c_int, ctypes.c_int
]

# ---------------- CLASSES --------------------------------
class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

class LOGFONTW(ctypes.Structure):
    _fields_ = [
        ("lfHeight", wintypes.LONG),
        ("lfWidth", wintypes.LONG),
        ("lfEscapement", wintypes.LONG),
        ("lfOrientation", wintypes.LONG),
        ("lfWeight", wintypes.LONG),
        ("lfItalic", wintypes.BYTE),
        ("lfUnderline", wintypes.BYTE),
        ("lfStrikeOut", wintypes.BYTE),
        ("lfCharSet", wintypes.BYTE),
        ("lfOutPrecision", wintypes.BYTE),
        ("lfClipPrecision", wintypes.BYTE),
        ("lfQuality", wintypes.BYTE),
        ("lfPitchAndFamily", wintypes.BYTE),
        ("lfFaceName", wintypes.WCHAR * LF_FACESIZE),
    ]
    
class DRAWITEMSTRUCT(ctypes.Structure):
    _fields_ = [
         ("CtlType", wintypes.UINT),
        ("CtlID", wintypes.UINT),
        ("itemID", wintypes.UINT),
        ("itemAction", wintypes.UINT),
        ("itemState", wintypes.UINT),
        ("hwndItem", wintypes.HWND),
        ("hDC", wintypes.HDC),
        ("rcItem", wintypes.RECT),
        ("itemData", wintypes.LPARAM),
    ]