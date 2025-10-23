
#try:
  #  from pharmacy_v1.config.environment import admin_password
#except Exception:
   # from config.environment import admin_password

import json
from getpass import getpass
from datetime import datetime
from pathlib import Path

# Optional colors for terminal output
try:
    from colorama import Fore, Style, init as _colorama_init
    _colorama_init(autoreset=True)
except Exception:
    Fore = None
    Style = None

# Optional payment sound
try:
    from playsound import playsound
except Exception:
    playsound = None


def play_sound():
    """Play applepay.wav using AppKit.NSSound on macOS, fallback to playsound.

    Swallows all exceptions to avoid breaking checkout flow.
    """
    # First attempt: AppKit (PyObjC)
    try:
        from AppKit import NSSound
        module_file = Path(__file__).resolve().parent / "applepay.wav"
        cwd_file = Path("applepay.wav")
        sound_path = module_file if module_file.exists() else (cwd_file if cwd_file.exists() else None)
        if sound_path:
            ns = NSSound.alloc().initWithContentsOfFile_byReference_(str(sound_path.resolve()), True)
            if ns:
                ns.play()
                return
    except Exception:
        # AppKit not available or playback failed; fall through to fallback
        pass

    # Fallback: playsound if installed
    try:
        if playsound:
            snd = Path("applepay.wav")
            if not snd.exists():
                snd = Path(__file__).resolve().parent / "applepay.wav"
            if snd.exists():
                playsound(str(snd.resolve()))
    except Exception:
        pass


# load inventory from the json file that contains the data
inv_path = Path("inventory.json")
if not inv_path.exists():
    inv_path = Path(__file__).resolve().parent / "inventory.json"

def reload_inventory():
    global inventory
    with open(inv_path, "r") as f:
        inventory = json.load(f)


def save_inventory():
    """Persist the in-memory inventory back to the inventory.json file (inv_path)."""
    global inventory
    try:
        # Ensure parent directory exists for inv_path
        inv_path.parent.mkdir(parents=True, exist_ok=True)
        with open(inv_path, "w", encoding="utf-8") as f:
            json.dump(inventory, f, indent=2, ensure_ascii=False)
    except Exception as e:
        # Bubble up the exception so callers can decide how to handle it
        raise

# initial load
reload_inventory()

cart = {}
orders = {}
order_id_counter = 1

def find_item_container(name):
    """Return (container_dict, key) where the item is stored, or (None, None).
    Lookup is case-insensitive and supports both flat and category->items layouts."""
    if not name:
        return None, None
    target = name.lower()
    # flat layout detection: items at top level having 'price'
    for k, v in list(inventory.items()):
        if isinstance(v, dict) and 'price' in v:
            if k.lower() == target:
                return inventory, k
    # nested categories
    for cat, items in inventory.items():
        if not isinstance(items, dict):
            continue
        for k, v in items.items():
            if k.lower() == target:
                return items, k
    return None, None

def list_medicines():
    # Reload inventory from disk so external edits are reflected immediately
    reload_inventory()
    print("\nAvailable Medicines:")
    # Detect whether inventory is flat (item->info) or nested (category->items)
    flat = all(isinstance(v, dict) and 'price' in v for v in inventory.values())
    if flat:
        for name, info in inventory.items():
            qty = info.get('quantity', 0)
            low_warn = " \u26a0 Low stock" if qty < 5 else ""
            print(f"- {name} | Price: {info['price']} | Qty: {qty} | Expiry: {info['expiry']}{low_warn}")
    else:
        # grouped by category
        for cat, items in inventory.items():
            if not isinstance(items, dict):
                continue
            print(f"\nCategory: {cat}")
            for name, info in items.items():
                qty = info.get('quantity', 0)
                low_warn = " \u26a0 Low stock" if qty < 5 else ""
                print(f"- {name} | Price: {info['price']} | Qty: {qty} | Expiry: {info['expiry']}{low_warn}")
    print()

def search_medicine(name):
    container, key = find_item_container(name)
    # Prepare display name
    display_name = (key if key else name).replace('_', ' ').title() if name else ""

    if container:
        info = container[key]
        price = info.get('price', 0)
        qty = info.get('quantity', 0)
        expiry = info.get('expiry', '')

        # Build lines for the box
        title = f"💊  Medicine Found: {display_name}"
        line_price = f"💰 Price:     {price} SAR"
        line_qty = f"📦 Quantity:  {qty} units"
        line_exp = f"⏳ Expiry:    {expiry}"

        content_lines = [ title, line_price, line_qty, line_exp]

        # Compute width based on longest line (no ANSI present yet)
        width = max(len(l) for l in content_lines)
        # Decorative horizontal
        h = '─' * width

        # Color choice for available
        color = Fore.GREEN if Fore else ''
        reset = Style.RESET_ALL if Style else ''

        print()
        print(color + h + reset)
        for l in content_lines:
            # center title, left-align fields
            if l == title:
                pad_left = (width - len(l)) // 2
                print(color + ' ' * pad_left + l + ' ' * (width - pad_left - len(l)) + reset)
            else:
                # left align non-empty, blank lines print as-is
                if l.strip() == '':
                    print(color + ' ' * width + reset)
                else:
                    print(color + l.ljust(width) + reset)
        print(color + h + reset + "\n")
    else:
        # Not found -- red box
        header = f"🔍 Medicine not found: {name.replace('_',' ').title()}"
        lines = ["", header, "", "Please check the name and try again.", ""]
        width = max(len(l) for l in lines)
        h = '─' * width
        color = Fore.RED if Fore else ''
        reset = Style.RESET_ALL if Style else ''

        print()
        print(color + h + reset)
        for l in lines:
            if l.strip() == '':
                print(color + ' ' * width + reset)
            else:
                pad_left = (width - len(l)) // 2
                print(color + ' ' * pad_left + l + ' ' * (width - pad_left - len(l)) + reset)
        print(color + h + reset + "\n")

def add_to_cart(name, qty=1):
    """Add `qty` of `name` to the cart. Default qty=1.

    If the requested quantity exceeds available stock, the operation is
    rejected and a helpful message is printed.
    """
    # normalize qty
    try:
        qty = int(qty)
    except Exception:
        print("\nQuantity must be a number.\n")
        return
    if qty <= 0:
        print("\nQuantity must be at least 1.\n")
        return

    # support case-insensitive lookup
    container, key = find_item_container(name)
    if not container:
        print("\nMedicine not available.\n")
        return

    available = int(container[key].get("quantity", 0))
    if available >= qty:
        cart[key] = cart.get(key, 0) + qty
        container[key]["quantity"] = available - qty
        print(f"\n{qty} x {key} added to cart.\n")
    else:
        print(f"\nNot enough stock for {key}. Available: {available}, requested: {qty}.\n")

def remove_from_cart(name):
    if name in cart:
        cart[name] -= 1
        container, key = find_item_container(name)
        if container and key in container:
            container[key]["quantity"] += 1
        if cart[name] <= 0:
            del cart[name]
        print(f"\n{name} removed from cart.\n")
    else:
        print("\nMedicine not in cart.\n")

def show_cart():
    if not cart:
        print("\nCart is empty.\n")
        return
    print("\nCart Items:")
    for name, qty in cart.items():
        print(f"- {name} x{qty}")
    print()

def checkout():
    global order_id_counter
    if not cart:
        print("\nCart is empty.\n")
        return
    # Calculate subtotal
    subtotal = 0.0
    for name, qty in cart.items():
        container, key = find_item_container(name)
        price = float(container[key]["price"]) if container and key in container else 0.0
        subtotal += price * qty

    # Apply automatic 10% discount
    discount = round(subtotal * 0.10, 2)
    final_total = round(subtotal - discount, 2)

    order_id = f"ORD{order_id_counter}"
    order_id_counter += 1
    # store final_total as the order total, keep items and status
    orders[order_id] = {"items": cart.copy(), "status": "Processing", "subtotal": round(subtotal, 2), "discount": discount, "total": final_total}

    cart.clear()
    print(f"\nOrder placed! Order ID: {order_id}")
    print(f"Subtotal: ${subtotal:.2f}")
    print(f"Discount (10%): -${discount:.2f}")
    print(f"Final amount: ${final_total:.2f}\n")
    # Play payment sound once (platform-specific with fallback)
    try:
        play_sound()
    except Exception:
        # play_sound is resilient, but guard anyway
        pass
    # Write a formatted, bordered invoice to disk
    try:
        items = orders[order_id]["items"]
        # Collect item rows with unit prices
        rows = []
        max_name = 0
        for name, qty in items.items():
            c, k = find_item_container(name)
            unit = float(c[k]["price"]) if c and k in c else 0.0
            line = round(unit * qty, 2)
            rows.append((name, unit, qty, line))
            if len(name) > max_name:
                max_name = len(name)

        # Column widths
        item_w = max(10, min(max_name, 30))
        unit_w = 8
        qty_w = 6
        line_w = 10
        gap = 4
        total_width = item_w + unit_w + qty_w + line_w + gap

        border_eq = '=' * total_width
        sep = '-' * total_width

        invoice_name = f"invoice_{order_id}.txt"

        # Ensure numeric types for safe formatting
        subtotal_val = float(round(subtotal, 2))
        discount_val = float(round(discount, 2))
        total_val = float(round(final_total, 2))

        # Prepare printable rows with typed numbers and display names
        printable_rows = []
        for name, unit, qty, line in rows:
            printable_rows.append((name.replace('_', ' ').title(), float(unit), int(qty), float(line)))

        # framed box parameters
        box_pad = 2  # spaces on left/right inside the box
        inner_width = total_width
        box_width = inner_width + box_pad * 2
        top_border = '+' + ('=' * box_width) + '+'
        sep_border = '|' + ('-' * box_width) + '|'
        empty_border = '|' + (' ' * box_width) + '|'

        title = "INVOICE RECEIPT 💊"
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Helper to build a boxed line (content will be padded/truncated to inner_width)
        def boxed_line(content: str) -> str:
            return '|' + (' ' * box_pad) + content.ljust(inner_width)[:inner_width] + (' ' * box_pad) + '|'

        # Build file contents (boxed)
        try:
            with open(invoice_name, 'w', encoding='utf-8') as f:
                f.write(top_border + '\n')
                f.write(boxed_line(title.center(inner_width)) + '\n')
                f.write('|' + ('=' * box_width) + '|' + '\n')

                f.write(boxed_line(f"Order ID: {order_id}") + '\n')
                f.write(boxed_line(f"Date: {now_str}") + '\n')
                f.write(sep_border + '\n')

                # header (build with explicit padding to avoid nested format edge cases)
                item_header = 'Item'.ljust(item_w)
                unit_header = 'Unit'.rjust(unit_w + 2)
                qty_header = 'Qty'.rjust(qty_w + 2)
                line_header = 'Line'.rjust(line_w + 2)
                header = item_header + unit_header + qty_header + line_header
                f.write(boxed_line(header) + '\n')
                f.write(sep_border + '\n')

                # rows
                for display, unit_val, qty_val, line_val in printable_rows:
                    item_str = str(display)[:item_w].ljust(item_w)
                    unit_str = f"{unit_val:.2f}".rjust(unit_w + 2)
                    qty_str = str(qty_val).rjust(qty_w + 2)
                    line_str = f"{line_val:.2f}".rjust(line_w + 2)
                    row = item_str + unit_str + qty_str + line_str
                    f.write(boxed_line(row) + '\n')
                    f.write(sep_border + '\n')

                # totals
                totals_pad = item_w + unit_w + qty_w + gap
                f.write(boxed_line('') + '\n')
                f.write(boxed_line(f"{'Subtotal:':<{totals_pad}}{subtotal_val:>{line_w+2}.2f}") + '\n')
                f.write(boxed_line(f"{'Discount (10%):':<{totals_pad}}-{discount_val:>{line_w+1}.2f}") + '\n')
                f.write(boxed_line(f"{'Total:':<{totals_pad}}{total_val:>{line_w+2}.2f}") + '\n')

                f.write(top_border + '\n')

            print(f"Invoice written to {invoice_name}")
        except Exception as e:
            print(f"Failed to write invoice: {e}")

        # Print the same framed invoice to the console
        try:
            print('\n' + top_border)
            print(boxed_line(title.center(inner_width)))
            print('|' + ('=' * box_width) + '|')
            print(boxed_line(f"Order ID: {order_id}"))
            print(boxed_line(f"Date: {now_str}"))
            print(sep_border)
            print(boxed_line(header))
            print(sep_border)
            for display, unit_val, qty_val, line_val in printable_rows:
                item_str = str(display)[:item_w].ljust(item_w)
                unit_str = f"{unit_val:.2f}".rjust(unit_w + 2)
                qty_str = str(qty_val).rjust(qty_w + 2)
                line_str = f"{line_val:.2f}".rjust(line_w + 2)
                row = item_str + unit_str + qty_str + line_str
                print(boxed_line(row))
                print(sep_border)

            print(boxed_line(''))
            left_sub = 'Subtotal:'.ljust(totals_pad)
            right_sub = f"{subtotal_val:.2f}".rjust(line_w + 2)
            print(boxed_line(left_sub + right_sub))

            left_disc = 'Discount (10%):'.ljust(totals_pad)
            right_disc = ('-' + f"{discount_val:.2f}").rjust(line_w + 2)
            print(boxed_line(left_disc + right_disc))

            left_tot = 'Total:'.ljust(totals_pad)
            right_tot = f"{total_val:.2f}".rjust(line_w + 2)
            print(boxed_line(left_tot + right_tot))
            print(top_border + '\n')
        except Exception:
            pass

        # persist inventory changes after successful checkout
        try:
            save_inventory()
        except Exception:
            # non-fatal if saving fails; user still has the invoice
            pass
    except Exception as e:
        print(f"Failed to write invoice: {e}")

    # (Audio playback removed by request)

def track_order(order_id):
    if order_id in orders:
        print(f"\nOrder {order_id} status: {orders[order_id]['status']}\n")
    else:
        print("\nOrder not found.\n")

