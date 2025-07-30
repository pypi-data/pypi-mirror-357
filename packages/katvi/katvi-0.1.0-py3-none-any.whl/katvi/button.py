from .window import Window
from . import core as C
import ctypes
from ctypes import wintypes

user32 = C.user32
gdi32 = C.gdi32
hwnd = None
style = C.WS_VISIBLE | C.WS_CHILD | C.BS_OWNERDRAW

class Button:
    def __init__(self, parent: Window, text="", x=None, y=None, width=100, height=30, dock=None):
        self.text = text
        self.dock = dock
        self.on_click = lambda: print(f"{text} was clicked!")
        self.hwnd = None
        self.parent = parent
        
        if dock is None and None not in (x, y):
            self.hwnd = user32.CreateWindowExW(
                0, "BUTTON", text,
                style,
                x, y, width, height,
                parent.hwnd, None, parent.hInstance, None
            )

        parent.add_control(self)

    def create(self, parent_hwnd, hInstance):
 
        if not self.hwnd:
            self.id = id(self) & 0xFFFF
            self.hwnd = user32.CreateWindowExW(
                0, "BUTTON", self.text,
                style,
                0, 0, 100, 30,  
                parent_hwnd, self.id, hInstance, None
            )
            
        lf = C.LOGFONTW()
        lf.lfHeight = -16  # Size in logical units
        lf.lfFaceName = "Segoe UI"
        font = gdi32.CreateFontIndirectW(ctypes.byref(lf))
        user32.SendMessageW(self.hwnd, C.WM_SETFONT, font, True)