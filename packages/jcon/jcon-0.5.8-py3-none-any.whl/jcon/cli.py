import argparse
from .layout import save_layout, load_layout
from .core import get_icon_count, get_icon_position, set_icon_position, get_desktop_listview

def main():
    parser = argparse.ArgumentParser(prog='jcon', description='Desktop Icon Mover Tool')
    parser.add_argument('--save', metavar='FILE', help='Save icon positions to a JSON file')
    parser.add_argument('--load', metavar='FILE', help='Load icon positions from a JSON file')
    parser.add_argument('--move', nargs=3, metavar=('INDEX', 'X', 'Y'), help='Move a specific icon by index')
    parser.add_argument('--print', action='store_true', help='Print icon positions')
    
    args = parser.parse_args()
    lv = get_desktop_listview()

    if args.save:
        save_layout(args.save)
        print(f"Saved layout to {args.save}")

    elif args.load:
        load_layout(args.load)
        print(f"Loaded layout from {args.load}")

    elif args.move:
        idx, x, y = map(int, args.move)
        set_icon_position(lv, idx, x, y)
        print(f"Moved icon {idx} to ({x},{y})")

    elif args.print:
        count = get_icon_count(lv)
        print(f"Found {count} icons:")
        for i in range(count):
            pos = get_icon_position(lv, i)
            print(f"Icon {i}: {pos}")

if __name__ == "__main__":
    main()
