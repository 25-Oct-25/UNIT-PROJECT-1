FitCoach CLI — دليل المستخدم
المتطلبات

Python ≥ 3.9 (مجرّب على 3.13)

حزم: colorama (للتلوين)، وfpdf (لتوليد PDF).

يُفضّل تفعيل بيئة افتراضيّة:

python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

تثبيت الحزم:
pip install colorama fpdf
# (أو عبر requirements.txt إن كان موجود)

التشغيل
python -m fitcoach_cli


خيارات الألوان:

تعطيل الألوان: python -m fitcoach_cli --no-color

إجبار الألوان: FORCE_COLOR=1 python -m fitcoach_cli

تعطيل عبر البيئة: NO_COLOR=1 python -m fitcoach_cli


بنية عامة

اكتب أمرًا ثم Enter.

للخروج: exit أو quit أو q.

للمساعدة: help (يعرض دليلاً ملوّنًا).


الأوامر الرئيسية (سريع)
help | exit | quit | q
auth ...              إدارة المستخدمين والصلاحيات
profile ...           ملف المستخدم
calories calc         حساب السعرات والماكروز
plan ...              توليد/عرض برنامج التمرين وقياس الحجم
recipes ...           اقتراح أو بناء يوم وجبات
export csv ...        تصدير الخطة إلى CSV
advice daily          نصائح يومية
habits ...            تسجيل/تقييم العادات
nudge --type=...      تنبيه (ماء/نوم/خطوات/بروتين)
progress ...          تقدّم الوزن (تسجيل/تحليل/رسم ASCII)
workout ...           تسجيل تمرين أو اقتراح أوزان
report ...            توليد/إرسال/جدولة تقارير أسبوعية PDF
email ...             إعداد واختبار البريد
app lang --set=ar|en  لغة الواجهة


--------------------------------------------------------------------------------------------------------------------------

1- أوامر الصلاحيات: auth

ملاحظة أمنية: أول مستخدم يُنشأ دون شرط الدور. بعد ذلك، الأوامر الإدارية تتطلب دور admin.

إضافة مستخدم:



تسجيل الدخول/الخروج وهوية الدور:

auth login --username=admin --password=secret
auth logout
auth whoami


إدارة الأدوار والمستخدمين:


auth list-users
auth role set --username=user1 --role=coach
auth delete-user --username=user1

--------------------------------------------------------------------------------------------------------------------------------
ملف المستخدم: profile
profile show
profile set --sex=male|female --age=22 --height=183 --weight=110 \
  --activity=sedentary|light|moderate|active|very_active \
  --goal=cut|bulk|recomp


  
السعرات والماكروز: calories
يحسب BMR/TDEE والهدف حسب الـ goal:

calories calc




خطة التمرين: plan
توليد/عرض/حجم:


plan generate --split=upper-lower|full-body|ppl --days=3..6
plan show
plan volume




قائمة المشتريات + تصدير CSV:


plan groceries --target=2400 --P=180 --C=250 --F=70 [--filters=chicken,rice]
export csv --file=week.csv



الوصفات والوجبات: recipes
اقتراح وصفات ضمن هدف:


recipes suggest --kcal=700 --protein=40 [--filters=chicken,rice]



بناء يوم كامل:

recipes build-day --target=2400 --P=180 --C=250 --F=70 [--filters=chicken,rice]



نصائح وعادات: advice و habits و nudge
advice daily
habits log --water=3 --sleep=7.5 --steps=9000
habits score
nudge --type=water|sleep|steps|protein



التقدّم (الوزن): progress
progress log --weight=108.5
progress analyze
progress plot



التمارين: workout
workout log --day=2 --ex="Bench Press" --weight=80 --reps=8 --RPE=8
workout suggest --ex="Bench Press"



التقارير (PDF) والبريد والجدولة: report و email

توليد PDF أسبوعي:

report pdf --file=week_report.pdf --days=7



العلامة التجارية (Admin فقط):

report brand --title="FitCoach — Weekly Report" --color=#0A84FF --logo=./logo.png



إرسال التقرير عبر البريد:

email config --to=user@example.com [--from=coach@fitcoach.dev]
report send --file=week_report.pdf --subject="FitCoach — Weekly Report" --text="ملخص أسبوعك جاهز"



جدولة إرسال أسبوعي (Admin فقط):

report schedule add --time=21:00 --day=Sun --file=week_report.pdf --text="ملخص أسبوعك جاهز" --days=7
report schedule list
report schedule remove --id=1



اختبار البريد:

email test --subject="Test" --text="Hello from FitCoach"



لغة الواجهة: app
app lang --set=ar
# أو
app lang --set=en