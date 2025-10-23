import json
import os
from rich.console import Console
from rich.table import Table
from email_service import send_email

console = Console() 
CAMPAIGNS_FILE = "campaigns.json" #اسم الملف الذي سيتم حفظ الحملات فيه


#Load all campaigns from the JSON file.
def load_campaigns(): #تتحقق أولاً إذا كان الملف موجودًا،
    if not os.path.exists(CAMPAIGNS_FILE):
        return []
    try:
        with open(CAMPAIGNS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:# اذا الملف تالف
        return []
    
#Save campaigns to the JSON file
def save_campaigns(campaigns):#تحفظ قائمة الحملات
    with open(CAMPAIGNS_FILE, "w") as f:
        json.dump(campaigns, f, indent=4)


#Show all campaigns in a table
def display_campaigns():#عرض جميع الحملات
    campaigns = load_campaigns()
    if not campaigns:
        console.print("⚠️"" No campaigns available.", style="#c67a7a")
        return
    #انشاء الجداول 
    table = Table(
      title=" Campaigns List ✈️", 
      title_style="bold bright_white", 
      show_lines=True,
      width=150
)    
    table.add_column("ID", justify="center", header_style="#8773a1", no_wrap=True, width=8)
    table.add_column("Leader Email", header_style="#8773a1", no_wrap=False, width=20)
    table.add_column("Airline", header_style="#8773a1", no_wrap=False, width=15)
    table.add_column("Flight", header_style="#8773a1", no_wrap=True, width=12)
    table.add_column("From", header_style="#8773a1", no_wrap=False, width=18)
    table.add_column("To", header_style="#8773a1", no_wrap=False, width=18)
    table.add_column("Departure", header_style="#8773a1", no_wrap=True, width=20)
    table.add_column("Members", header_style="bold #8773a1", no_wrap=True, width=20)

    for c in campaigns:#لكل حملة: تحسب عدد الأعضاء المتبقيين، وتعرض بيانات الحملة في صف الجدول.
        members_info = f"({len(c['members'])}/{c['max_members']})"
        table.add_row(
            str(c['id']),
            c['leader'],
            c['airline'],
            c['flight_number'],
            c['from'],
            c['to'],
            c['departure_time'],
            members_info
        )
    console.print(table)


# Add a new campaign to the system
def add_campaign(leader=None):#دالة إضافة حملة جديدة
    campaigns = load_campaigns()#تحميل الحملات الحالية
    next_id = 1 if not campaigns else max(c['id'] for c in campaigns) + 1

    leader_name = leader or input("Leader name 👤: ")# # اسم القائد (إذا موجود كوسيط يتم استخدامه)
    from_place = input("Departure from 🛫 : ").strip()
    if not from_place:
       console.print("⚠️""  Departure cannot be empty.", style="#c67a7a")
       return
    to_place = input("Destination 🛬 : ").strip()
    if not to_place:
        console.print("⚠️""  Destination cannot be empty.", style="#c67a7a")
        return
    airline = input("Airline ✈️ : ").strip()
    if not airline:
        console.print("⚠️""  Airline cannot be empty.", style="#c67a7a")
        return
    flight_number = input("Flight number 🎟️: ").strip()
    if not flight_number:
        console.print("⚠️""  Flight number cannot be empty.", style="#c67a7a")
        return
    departure_time = input("Departure time (YYYY-MM-DD HH:MM) 🕒: ")
    max_members = input("Max members 👥 : ")

    if not max_members.isdigit() or int(max_members) <= 0: # التحقق من صحة الرقم
        console.print("⚠️""  Max members must be a positive number.", style="#c67a7a")
        return
    
    #  # إنشاء قاموس للحملة الجديدة
    campaign = {
        "id": next_id,
        "leader": leader_name,
        "from": from_place,
        "to": to_place,
        "airline": airline,
        "flight_number": flight_number,
        "departure_time": departure_time,
        "max_members": int(max_members),
        "members": []  # قائمة الأعضاء فارغة عند الإنشاء
    }
    campaigns.append(campaign)#  إضافة الحملة للقائمه
    save_campaigns(campaigns)# حفظ القائمة في الملف
    console.print("✅ Campaign added successfully!", style="#8EA891")



# Register a member to a campaign
def join_campaign(member_name, member_email):# دالة للانضمام لحملة
    if len(member_name.strip().split()) < 2: # التحقق من الاسم الكامل (اسم ولقب)
        console.print("⚠️"" Name must include first and last name.", style="#c67a7a")
        return
    
    campaigns = load_campaigns()  # تحميل الحملات
    for c in campaigns:  # التحقق إذا العضو مسجل مسبقًا
        if any(m['email'] == member_email for m in c['members']):
            console.print(f"⚠️ Already registered in Campaign ID {c['id']}.", style="#c67a7a")
            return
        

    display_campaigns()  # عرض الحملات للمستخدم
    camp_id_input = input("Enter Campaign ID to join: ")# إدخال رقم الحملة
    if not camp_id_input.isdigit():#مهي موجوده
        console.print("⚠️"" Invalid ID entered.", style="#c67a7a")
        return
    
    camp_id = int(camp_id_input)  # تحويل الرقم إلى عدد صحيح
    campaign = next((c for c in campaigns if c['id'] == camp_id), None) # البحث عن الحملة
    if not campaign:#اذا مهي موجوده
        console.print("⚠️"" Campaign not found.", style="#c67a7a")
        return
    
    if len(campaign['members']) >= campaign['max_members']:# إذا كانت الحملة ممتلئة
        console.print("⚠️"" Campaign is full.", style="#c67a7a")
        return
    
    campaign['members'].append({"name": member_name, "email": member_email}) # إضافة العضو
    save_campaigns(campaigns)#حفظ التغييرات
    console.print(f"✅ Successfully joined Campaign ID {camp_id}.", style="#8cc98e")
    send_email(member_email, "Campaign Joined", f"Hello {member_name}, you joined campaign '{campaign['airline']} {campaign['flight_number']}' successfully!")# إرسال بريد تأكيد


# Display all members of the leader's campaigns
def display_campaign_members(leader_email): # دالة لعرض أعضاء الحملة للقائد
    campaigns = load_campaigns() # تحميل الحملات
    leader_campaigns = [c for c in campaigns if c['leader'] == leader_email]# تصفية الحملات للقائد
    if not leader_campaigns:# إذا لا توجد حملات
        console.print("⚠️"" You have no campaigns.", style="#c67a7a")
        return
    
    for c in leader_campaigns:# لكل حملة للقائد
        console.print(f"\n🛫 Campaign '{c['airline']} {c['flight_number']}' (ID: {c['id']})")# إذا لا يوجد أعضاء
        if not c.get('members'):
            console.print("   No members yet.", style="#c67a7a")

        else:
            for i, m in enumerate(c['members'], 1):# عرض كل عضو برقم وترتيب
                console.print(f"   {i}. {m['name']} - {m['email']}")
