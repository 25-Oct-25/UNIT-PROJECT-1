services = {        # انشات daicitionary  من اجل تعريف كل نوع وسعره 
    "chibi": 50,
    "head_only": 40,
    "sketch": 30,
    "half_body": 80,
    "full_body": 100,
    "full_body_bg": 130
}

def list_services():
    print("\n🖌️ Available Art Services:\n") # خدمات الفنية المتاحة
    for name, price in services.items():
        print(f"- {name.replace('_', ' ').title():20} : {price} SAR") # لوب للطباعه

def choose_service(service_name:str, is_additional=False):
    """Choose a service and calculate final price with discount"""
    service_name = service_name.lower() #  
    if service_name not in services:
        print("\n❌ Service not found. Use 'list_services' to see all available ones.")
        return None

    base_price = services[service_name:str]
    discount = 0
    final_price = base_price

    # If this is an additional service, apply 50% discount
    if is_additional:
        discount = base_price / 2
        final_price = base_price - discount

    print(f"\n✅ '{service_name}' selected ({base_price} SAR).")
    if discount:
        print(f"💸 Discount applied: {discount} SAR | Final Price: {final_price} SAR")

    return {
        "service": service_name,
        "price": base_price,
        "discount": discount,
        "final_price": final_price
    }
