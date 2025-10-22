import os
from datetime import datetime
from colorama import Fore, Style

def checkout(cart, customer_name, payment_method, notes):
    if not cart:
        print(Fore.RED + "🛒 Cart is empty!" + Style.RESET_ALL)
        return 0, ""

    total = sum(item["final_price"] for item in cart)

    invoice_lines = [f"🖌️ Invoice for {customer_name}", "-"*40]
    for item in cart:
        invoice_lines.append(
            f"{item['service'].replace('_',' ').title():20} | Base: {item['price']:5} SAR | Discount: {item['discount']:5} | Final: {item['final_price']:5} SAR"
        )

    invoice_lines.append("-"*40)
    invoice_lines.append(f"Total: {total} SAR")
    invoice_lines.append(f"Payment method: {payment_method}")
    invoice_lines.append(f"Notes: {notes}")
    invoice_lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    invoice_text = "\n".join(invoice_lines)
    print(Fore.GREEN + f"\n✅ Order confirmed successfully!\n💰 Total: {total} SAR | Payment: {payment_method}" + Style.RESET_ALL)
    return total, invoice_text
