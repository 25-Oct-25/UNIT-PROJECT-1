import webbrowser  # استيراد من مكتبة ال pillow  لاجل عرض الصور

gallery = {
    "chibi": [
        "https://i.top4top.io/p_3581ke5o51.jpeg",
        "https://i.top4top.io/p_3581ke5o51.jpeg"
    ],
    "half_body": [
        "https://d.top4top.io/p_3581e18a31.jpeg",
        "https://d.top4top.io/p_3581e18a31.jpeg"# نص جسم
    ],
    "full_body": [
        "https://k.top4top.io/p_35813jq8i1.jpeg"# جسم كامل
    ],
    "full_body_bg": [
        "https://d.top4top.io/p_35810wunv1.jpeg"# جسم كامل مع خلفية
    ],
    "sketch": [
        "https://k.top4top.io/p_35813x8871.png"# سكتش فقط بدون تلوين 
    ],
    "head_only": [
        "https://d.top4top.io/p_3581v6wwl1.png" # راس فقط
    ]
}


def show_gallery(category=None): # عرفت الدالة وذكرت انه اذا مامرر اي قيمة فيطلع له none
    if not category: #اذا ماحدد نوع طلبه  الدالة تطلب منه  يحدد النوع 
        print("\nPlease specify a category (e.g., show_gallery chibi)")
        print("Available categories:", ", ".join(gallery.keys()))
        return # عملية ارجاع لاجل انهاء اذا هو ماحدد فئة الخدمة

    category = category.lower()
    if category not in gallery: # هنا مثلا لو طلب خدمة مو موجودة عندي مثلا سكتش ملون  مو موجوده تخبره انه الخدمة غير موجود
        print(f"\n❌ '{category}' not found in gallery categories.")
        print("Available categories:", ", ".join(gallery.keys()))
        return

    print(f"\n🎨 Showing samples for '{category}':")
    for i, link in enumerate(gallery[category], 1):
        print(f"{i}. {link}")
        webbrowser.open(link)  # يفتح الصورة في المتصفح لما يحدد نوع الي يبي يشوفه 
