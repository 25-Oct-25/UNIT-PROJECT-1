# show_orders.py
import json
from tabulate import tabulate
from colorama import Fore, Style
import os
from datetime import datetime 
def show_orders(customer_name): # تحفظ جميع طلبات محفوظة لعميل 
    """Display all saved orders for a specific customer"""
    orders_path = f"data/{customer_name.replace(' ', '_').lower()}_orders.json"

    try:
        if not os.path.exists(orders_path):
            print(Fore.YELLOW + f"📭 No orders found for {customer_name}." + Style.RESET_ALL)
            return

        with open(orders_path, "r", encoding="utf-8") as file:
            orders = json.load(file)

        if not orders:
            print(Fore.YELLOW + f"📭 {customer_name} has no orders yet." + Style.RESET_ALL)
            return

        for idx, order in enumerate(orders, 1):
            print(Fore.CYAN + f"\n📋 Order #{idx} for {customer_name}:\n" + Style.RESET_ALL)

            table_data = []
            for item in order.get("cart", []):
                base = item.get("price", 0)
                discount = item.get("discount", 0)
                final = item.get("final_price", base)
                table_data.append([
                    item.get("service", "").title(),
                    base,
                    discount,
                    final
                ])

            headers = ["Service", "Base Price (SAR)", "Discount", "Final Price (SAR)"]
            print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

            # Show order summary
            print(Fore.GREEN + f"Total: {order.get('final_price', 0)} SAR" + Style.RESET_ALL)
            print(Fore.YELLOW + f"Payment method: {order.get('payment', 'N/A')}" + Style.RESET_ALL)
            print(Fore.MAGENTA + f"Notes: {order.get('notes', '')}" + Style.RESET_ALL)
            print(Fore.WHITE + f"Date: {order.get('date', '')}" + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + f"⚠️ Error loading orders: {e}" + Style.RESET_ALL)
