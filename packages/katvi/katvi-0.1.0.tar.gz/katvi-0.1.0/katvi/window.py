import ctypes
from ctypes import wintypes
from . import core as C
import os

ctypes.windll.shcore.SetProcessDpiAwareness(1)

wintypes.WPARAM = ctypes.c_uint64
wintypes.LPARAM = ctypes.c_int64
icon_path = os.path.abspath("katvil.ico")
print("Rsolver icon path:", icon_path)

class PAINTSTRUCT(ctypes.Structure):
    _fields_ = [
        ("hdc", wintypes.HDC),
        ("fErase", wintypes.BOOL),
        ("rcPaint", wintypes.RECT),
        ("fRestore", wintypes.BOOL),
        ("fIncUpdate", wintypes.BOOL),
        ("rgbReserved", wintypes.BYTE * 32),
    ]

user32 = C.user32
gdi32 = C.gdi32
wintypes.LRESULT = ctypes.c_ssize_t
WNDPROCTYPE = ctypes.WINFUNCTYPE(
        wintypes.LRESULT,
        wintypes.HWND,
        wintypes.UINT,
        wintypes.WPARAM,
        wintypes.LPARAM)

class Window:
    def __init__(self, title="Katvi Window", width=500, height=300):
        self.hInstance = C.kernel32.GetModuleHandleW(None)
        self.text = ""
        self.className = "KatviWindowClass"
        self.text_align = "left"
        self.hwnd = None
        self.controls = []
        self.theme = ""
        
        self._register_class()
        self._create_window(title, width, height)
        
    def _register_class(self):
        WNDCLASS = type('WNDCLASS', (ctypes.Structure,), {
            '_fields_': [
                 ("style", wintypes.UINT),
                ("lpfnWndProc", WNDPROCTYPE),
                ("cbClsExtra", ctypes.c_int),
                ("cbWndExtra", ctypes.c_int),
                ("hInstance", wintypes.HINSTANCE),
                ("hIcon", wintypes.HICON),
                ("hCursor", wintypes.HCURSOR),
                ("hbrBackground", wintypes.HBRUSH),
                ("lpszMenuName", wintypes.LPCWSTR),
                ("lpszClassName", wintypes.LPCWSTR)
            ]
        })
        
        wndclass = WNDCLASS()
        
        def wnd_proc(hwnd, msg, wparam, lparam):
            if msg == C.WM_PAINT:
                ps = PAINTSTRUCT()
                hdc = user32.BeginPaint(hwnd, ctypes.byref(ps))
                
                if self.theme == "dark":
                    brush = gdi32.CreateSolidBrush(0x00202020)
                    text_color = 0x00FFFFFF
                else:
                    brush = gdi32.CreateSolidBrush(0x00FFFFFF)
                    text_color = 0x00000000
                    
                user32.FillRect(hdc, ctypes.byref(ps.rcPaint), brush)
                gdi32.SetTextColor(hdc, text_color)
                
                text_align = "left"
                if self.text_align == "center":
                    rect = C.RECT()
                    user32.GetClientRect(hwnd, ctypes.byref(rect))
                    text_width = len(text) * 8
                    x = (rect.right - text_width) // 2
                else:
                    x = 50
                text = self.text
                gdi32.TextOutW(hdc, x, 50, text, len(text))
                user32.EndPaint(hwnd, ctypes.byref(ps))
                return 0
            elif msg == C.WM_COMMAND:
                ctrl_id = wparam & 0xFFFF
                notif_code = (wparam >> 16) & 0xFFFF
                
                if notif_code == C.BN_CLICKED:
                    for ctrl in self.controls:
                        if hasattr(ctrl, "id") and ctrl.id == ctrl_id:
                            ctrl.on_click()
                    return 0
            elif msg == C.WM_DESTROY:
                user32.PostQuitMessage(0)
                return 0
            elif msg == C.WM_DRAWITEM:
                dis = ctypes.cast(lparam, ctypes.POINTER(C.DRAWITEMSTRUCT)).contents
                hdc = dis.hDC

                ctrl = next((c for c in self.controls if getattr(c, "hwnd", None) == dis.hwndItem), None)
                if not ctrl or not hasattr(ctrl, "text"):
                    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

                text = getattr(ctrl, "text", "")
                is_pressed = dis.itemState & C.ODS_SELECTED
                shadow_offset = 2 if not is_pressed else 0

                gdi32.SetBkMode(hdc, C.TRANSPARENT)

                # 1. Shadow rectangle (drawn *behind* everything)
                shadow_rect = C.RECT(
                    dis.rcItem.left - 3,
                    dis.rcItem.top - 3,
                    dis.rcItem.right + 3,
                    dis.rcItem.bottom + 4
                )
                shadow_brush = gdi32.CreateSolidBrush(0x00404040)
                user32.FillRect(hdc, ctypes.cast(ctypes.byref(shadow_rect), ctypes.POINTER(wintypes.RECT)), shadow_brush)


                # 2. Button background
                bg_color = 0x00C0C0C0 if not is_pressed else 0x00A0A0A0
                bg_brush = gdi32.CreateSolidBrush(bg_color)
                gdi32.SelectObject(hdc, bg_brush)
                gdi32.RoundRect(
                        hdc,
                        dis.rcItem.left,
                        dis.rcItem.top,
                        dis.rcItem.right,
                        dis.rcItem.bottom,
                        12, 12  # width, height of the rounded corners
                )
                # 3. Border
                user32.FrameRect(hdc, ctypes.cast(ctypes.byref(dis.rcItem), ctypes.POINTER(wintypes.RECT)), gdi32.GetStockObject(C.BLACK_BRUSH))
                
                size = ctypes.c_int()
                gdi32.GetTextExtentPoint32W(hdc, text, len(text), ctypes.byref(size))
                text_width = size.value
                rect_width = dis.rcItem.right - dis.rcItem.left
                rect_height = dis.rcItem.bottom - dis.rcItem.top
                x = dis.rcItem.left + (rect_width - text_width) // 2
                y = dis.rcItem.top + (rect_height - 16) // 2
                
                # 5. Main text
                gdi32.SetTextColor(hdc, 0x00000000)
                gdi32.TextOutW(hdc, x, y, text, len(text))

                return 1
            
            return user32.DefWindowProcW(
                hwnd,
                ctypes.wintypes.UINT(msg),
                ctypes.wintypes.WPARAM(wparam),
                ctypes.wintypes.LPARAM(lparam)
                )
        
        self._wnd_proc = WNDPROCTYPE(wnd_proc)
        
        wndclass.style = C.CS_HREDRAW | C.CS_VREDRAW
        wndclass.lpfnWndProc = self._wnd_proc
        wndclass.cbClsExtra = wndclass.cbWndExtra = 0
        wndclass.hInstance = self.hInstance
        wndclass.hCursor = user32.LoadCursorW(None, 32512)
        wndclass.hbrBackground = gdi32.GetStockObject(0)
        wndclass.lpszMenuName = None
        wndclass.lpszClassName = self.className
        wndclass.hIcon = user32.LoadImageW(
            None,
            r"C:\Users\andre\Downloads\Thonny\katvi\katviLm.ico",
            C.IMAGE_ICON,
            0, 0,
            C.LR_LOADFROMFILE | C.LR_DEFAULTSIZE
        )
                
        user32.RegisterClassW(ctypes.byref(wndclass))
        
    def _create_window(self, title, width, height):
        self.client_rect = C.RECT()
        
        self.hwnd = user32.CreateWindowExW(
            0, self.className, title,
            C.WS_OVERLAPPEDWINDOW,
            100, 100, width, height,
            None, None, self.hInstance, None)
        icon_handle = user32.LoadImageW(
            None, r"C:\Users\andre\Downloads\Thonny\katvi\katviLm.ico",
            C.IMAGE_ICON, 0, 0,
            C.LR_LOADFROMFILE | C.LR_DEFAULTSIZE
        )
        
        user32.SendMessageW(self.hwnd, C.WM_SETICON, C.ICON_BIG, icon_handle)
        user32.SendMessageW(self.hwnd, C.WM_SETICON, C.ICON_SMALL, icon_handle) 
        
        user32.RedrawWindow(self.hwnd, None, None, 0x0001 | 0x0002)
        user32.UpdateWindow(self.hwnd)
        
        user32.GetClientRect(self.hwnd, ctypes.byref(self.client_rect))
        
        print("ICON LOADED:", bool(icon_handle))
        
    def add_control(self, control):
        if not control.hwnd:
            control.create(self.hwnd, self.hInstance)
        self.controls.append(control)

    def show(self):
        user32.ShowWindow(self.hwnd, C.SW_SHOW)
        user32.UpdateWindow(self.hwnd)
        self.layout_controls()
        
    def run(self):
        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) !=0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
    
    def layout_controls(self):
        self.client_rect = C.RECT()
        user32.GetClientRect(self.hwnd, ctypes.byref(self.client_rect))
        padding_top = 0
        padding_bottom = 0
        
        for ctrl in self.controls:
            if ctrl.dock == "top":
                user32.SetWindowPos(ctrl.hwnd, None,
                                     0, padding_top,
                                     self.client_rect.right, 50,
                                     C.SWP_NOZORDER)
                padding_top += 50
            elif ctrl.dock == "bottom":
                user32.SetWindowPos(ctrl.hwnd, None,
                                    0, self.client_rect.bottom - 50 - padding_bottom,
                                    self.client_rect.right, 50,
                                    C.SWP_NOZORDER)
                padding_bottom += 50
            elif ctrl.dock == "center":
                width = 200
                
                height = 50
                
                x = (self.client_rect.right - width) // 2
                y = (self.client_rect.bottom - height) // 2
                user32.SetWindowPos(ctrl.hwnd, None, x, y, width, height, C.SWP_NOZORDER)