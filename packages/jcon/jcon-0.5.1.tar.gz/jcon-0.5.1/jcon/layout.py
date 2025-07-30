import json
from .core import get_icon_count, get_icon_position, set_icon_position, get_desktop_listview, JConError

def save_layout(filepath):
    try:
        listview = get_desktop_listview()
        count = get_icon_count(listview)
        positions = [get_icon_position(listview, i) for i in range(count)]
        with open(filepath, 'w') as f:
            json.dump(positions, f)
    except Exception as e:
        raise JConError(f"[JCON:] Failed to save layout: {e}")

def load_layout(filepath):
    try:
        listview = get_desktop_listview()
        with open(filepath, 'r') as f:
            positions = json.load(f)
        count = get_icon_count(listview)
        for i, (x, y) in enumerate(positions):
            if i >= count:
                break
            set_icon_position(listview, i, x, y)
    except Exception as e:
        raise JConError(f"[JCON:] Failed to load layout: {e}")
