# main.py
import os # هنا من اجل التعامل مع الملفات في حال التعديل او القراءة
import json # لاجل حفظ البيانات بالمجلدات 
from colorama import Fore, Style # لاضافة الالوان  على لوح التحكم 
from gallery import show_gallery # لعرض الصور عند تحديد نوع الخدمة عن طريق روابط من مكتبات
from services import list_services, choose_service #
from cart import add_to_cart, show_cart, clear_cart
from checkout import checkout
from show_order import show_orders
from email_ella import send_email


def show_banner(): # دالة لعرض شعار المتجر 
    print(Fore.MAGENTA + """
=========================================
         Art Commission Store
=========================================
""" + Style.RESET_ALL)


def show_menu(): # دالة لعرض الخدمات عبى الواجهة
    print(Fore.CYAN + """
Menu:

1. Show Gallery 
2. List Services
3. Choose Service
4. Show Cart
5. Clear Cart
6. Checkout
7. Show Orders
8. Help
0. Exit
""" + Style.RESET_ALL)


def load_cart(customer_name): # تقوم بتحميل السلة  المخصصة للعميل نفسه اذا موجود
    """Load cart from file if exists"""
    file_path = f"data/{customer_name}_cart.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return []


def save_cart(customer_name, cart): # السلة الموجودة حاليا تحفظها بالملف
    """Save current cart to a file"""
    os.makedirs("data", exist_ok=True)
    with open(f"data/{customer_name}_cart.json", "w") as f:
        json.dump(cart, f, indent=4)


def main(): # هنا راح يبدا البرنامج يشتغل 
    os.makedirs("data", exist_ok=True)

    show_banner()
    customer_name = input(Fore.YELLOW + "Enter your name: " + Style.RESET_ALL).strip() # اول مايعمل  run ويطلع له الشعار 
    customer_email = input(Fore.YELLOW + "Enter your email: " + Style.RESET_ALL).strip()# راح يطلب منه الاسم والايميل عشان يحظ له طلبه ويرسلها له على ايميله 

    cart = load_cart(customer_name) # بعد مايكتب اسم العميل هنا يطلع له قائمة 
    show_menu()

    while True: # الحلقة هنا راح تستمر الى ان يوقفها بالبريك  خصوصا انها مرقمة  وكسرها بيكون عند الضغط ب 0
        choice = input(Fore.YELLOW + "Enter choice (0-8): " + Style.RESET_ALL).strip()

        if choice == "1":
            category = input("Enter gallery category (chibi, half_body, full_body, full_body_bg, sketch, head_only): ").strip()
            show_gallery(category if category else None)

        elif choice == "2":
            list_services()

        elif choice == "3":
            first_service = True
            while True:
                service_name = input("Enter service name to add (or 'done' to finish): ").strip()
                if service_name.lower() == "done":
                    break
                service = choose_service(service_name, is_additional=not first_service)
                if service:
                    add_to_cart(cart, service)
                    print(Fore.GREEN + f"✅ Added {service['service']} to cart." + Style.RESET_ALL)
                    first_service = False
            save_cart(customer_name, cart)

        elif choice == "4":
            show_cart(cart)

        elif choice == "5":
            clear_cart(cart)
            save_cart(customer_name, [])
            print(Fore.YELLOW + "Cart cleared." + Style.RESET_ALL)

        elif choice == "6":
            if not cart:
                print(Fore.RED + "❌ Your cart is empty!" + Style.RESET_ALL)
                continue

            customer_notes = input("Enter any notes for your order (or leave empty): ").strip()
            payment_method = input("Choose payment method (cash / bank / visa): ").strip().lower()

            if payment_method == "visa": # هنا حطيت عملية انه اذا اختار دفع بالفيزة يحط اخر اربعه ارقام من البطاقة
                card_number = input("Enter last 4 digits of your Visa card: ").strip()
            elif payment_method == "bank":
                print("Please transfer to Account: 1234-5678-9999 and provide receipt via email.")
                card_number = "Bank Transfer"
            else:
                card_number = "Cash on Delivery"

            # Proceed with checkout
            total, invoice_text = checkout(cart, customer_name, payment_method, customer_notes)

            # Save invoice to file 
            invoice_path = f"data/{customer_name}_invoice.txt"
            with open(invoice_path, "w", encoding="utf-8") as f:
                f.write(invoice_text)
            print(Fore.GREEN + f"🧾 Invoice saved: {invoice_path}" + Style.RESET_ALL)

            # Auto email confirmation
            sender_email = input("Enter your sender email: ").strip()
            sender_password = input("Enter your email password (App Password if Gmail): ").strip()
            try:
                send_email(sender_email, sender_password, customer_email, "Your Art Commission Invoice", invoice_text)
            except Exception as e:
                print(Fore.RED + f"❌ Failed to send invoice email: {e}" + Style.RESET_ALL)
            
        



            show_cart(cart)

        elif choice == "7":
            show_cart(cart)

        elif choice == "8":
            show_menu()

        elif choice == "0":
            print(Fore.GREEN + "\nThank you for visiting! See you again soon." + Style.RESET_ALL)
            break

        else:
            print(Fore.RED + "❌ Invalid choice. Enter a number between 0-8." + Style.RESET_ALL)


if __name__ == "__main__":
    main()
