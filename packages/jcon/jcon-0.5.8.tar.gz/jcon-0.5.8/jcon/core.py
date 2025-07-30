import ctypes
from ctypes import wintypes

LVM_FIRST = 0x1000
LVM_GETITEMCOUNT = LVM_FIRST + 4
LVM_GETITEMPOSITION = LVM_FIRST + 16
LVM_SETITEMPOSITION = LVM_FIRST + 15

user32 = ctypes.WinDLL('user32', use_last_error=True)


class JConError(Exception):
    pass

class POINT(ctypes.Structure):
    _fields_ = [('x', wintypes.LONG), ('y', wintypes.LONG)]

def find_window(cls, title=None):
    hwnd = user32.FindWindowW(cls, title)
    if not hwnd:
        raise RuntimeError(f"[JCON:] Could not find window class '{cls}'")
    return hwnd

def find_window_ex(parent, child_after, cls, title=None):
    hwnd = user32.FindWindowExW(parent, child_after, cls, title)
    if not hwnd:
        raise RuntimeError(f"[JCON:] Could not find child window '{cls}'")
    return hwnd

def send_message(hwnd, msg, wparam, lparam):
    return user32.SendMessageW(hwnd, msg, wparam, lparam)

def get_desktop_listview():
    progman = find_window('Progman')
    try:
        defview = find_window_ex(progman, 0, 'SHELLDLL_DefView')
    except RuntimeError:
        workerw = find_window_ex(0, 0, 'WorkerW')
        defview = find_window_ex(workerw, 0, 'SHELLDLL_DefView')
    listview = find_window_ex(defview, 0, 'SysListView32')
    return listview

def get_icon_count(lv):
    count = send_message(lv, LVM_GETITEMCOUNT, 0, 0)
    if count < 0:
        raise RuntimeError("[JCON:] Failed to get icon count")
    return count

def get_icon_position(lv, idx):
    count = get_icon_count(lv)
    if idx < 0 or idx >= count:
        raise IndexError(f"[JCON:] Index {idx} out of range (0 to {count - 1})")
    pt = POINT()
    if not send_message(lv, LVM_GETITEMPOSITION, idx, ctypes.byref(pt)):
        raise RuntimeError(f"[JCON:] Failed to get position of icon {idx}")
    return pt.x, pt.y

def set_icon_position(lv, idx, x, y):
    count = get_icon_count(lv)
    if idx < 0 or idx >= count:
        raise IndexError(f"[JCON:] Index {idx} out of range (0 to {count - 1})")

    ICON_SPACING_X = user32.GetSystemMetrics(54)  
    ICON_SPACING_Y = user32.GetSystemMetrics(55)  
    x = (x // ICON_SPACING_X) * ICON_SPACING_X
    y = (y // ICON_SPACING_Y) * ICON_SPACING_Y

    pos = (y << 16) | (x & 0xFFFF)
    if not send_message(lv, LVM_SETITEMPOSITION, idx, pos):
        raise RuntimeError(f"[JCON:] Failed to set position of icon {idx}")

if __name__ == "__main__":
    lv = get_desktop_listview()
    n = get_icon_count(lv)
    print(f"Icons: {n}")
    for i in range(min(5, n)):
        print(f"Icon {i} pos:", get_icon_position(lv, i))
        set_icon_position(lv, i, 100 + i * 80, 100)
