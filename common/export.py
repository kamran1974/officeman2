from django.template.loader import get_template
from jalali_date_new.utils import datetime2jalali
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
import io
from django.conf import settings
import arabic_reshaper
from bidi.algorithm import get_display



TABLE_STYLE = TableStyle([
    ("FONTNAME", (0, 0), (-1, -1), "Vazirmatn"),  # استفاده از فونت فارسی
    ("BACKGROUND", (0, 0), (-1, 0), colors.gray),  # پس‌زمینه‌ی هدر
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),  # رنگ متن هدر
    ("ALIGN", (0, 0), (-1, -1), "RIGHT"),  # راست‌چین کردن متن
    ("VALIGN", (0, 0), (-1, -1), "TOP"),  # **بالاچین کردن متن**
    ("WORDWRAP", (0, 0), (-1, -1)),  # **فعال کردن شکستن متن در صورت طولانی بودن**
    ("BOTTOMPADDING", (0, 0), (-1, 0), 10),  # فاصله پایین هدر
    ("GRID", (0, 0), (-1, -1), 1, colors.black),  # خطوط جدول
])


'''
 * Not working for persian
 
def render_to_pdf(template_src: str,
                  context_dict: dict):

    template = get_template(template_src)
    html  = template.render(context_dict)

    buffer = io.BytesIO()

    # مسیر فونت فارسی
    font_path = os.path.join(settings.BASE_DIR, "static/fonts/Vazirmatn-Regular.ttf")

    # ثبت فونت فارسی در reportlab
    pdfmetrics.registerFont(TTFont("Vazirmatn", font_path))

    # تبدیل HTML به PDF با `Vazirmatn` به‌عنوان فونت پیش‌فرض
    pisa.CreatePDF(
        io.BytesIO(html.encode("UTF-8")),
        buffer,
        encoding="UTF-8",
        default_font="Vazirmatn",  # فونت ثبت‌شده
    )
    buffer.seek(0)

    return buffer
    
'''


def fix_persian_text(text):
    """ تابعی برای تبدیل متن فارسی به شکل صحیح در ReportLab """
    if text is None:
        return ""
    reshaped_text = arabic_reshaper.reshape(text)  # اصلاح اتصال حروف
    return get_display(reshaped_text)  # تنظیم راست به چپ


def generate_buy_order_pdf(logs):
    buffer = io.BytesIO()

    font_path = os.path.join(settings.BASE_DIR, "static/fonts/Vazirmatn-Regular.ttf")
    pdfmetrics.registerFont(TTFont("Vazirmatn", font_path))

    # ایجاد PDF
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    # **۱. ساخت هدر جدول**
    data = [["انجام شد", "وضعیت", "تاریخ", "توضیحات", "نوع", "تعداد", "برند", "نام کالا", "متقاضی"]]
    data = [[fix_persian_text(str(x)) for x in data[0]]]

    # **۲. اضافه کردن داده‌ها از دیتابیس**
    for log in logs:
        data.append([
            fix_persian_text(str("بله")) if log.completed else fix_persian_text(str("خیر")),
            fix_persian_text(str(log.status)),
            datetime2jalali(log.created).strftime("%Y/%m/%d - %H:%M"),
            fix_persian_text(str(log.description)) or fix_persian_text(str("بدون توضیحات")),
            fix_persian_text(str(log.order_type)),
            log.count,
            fix_persian_text(str(log.brand)),
            fix_persian_text(str(log.name)),
            fix_persian_text(str(log.user)),
        ])

    # **۳. ساخت جدول**
    table = Table(data, colWidths=[30, 70, 100, 100, 30, 20, 80, 80, 70])

    # **۴. تنظیم استایل‌های جدول**

    table.setStyle(TABLE_STYLE)

    # **۵. اضافه کردن جدول به PDF**
    elements.append(table)
    pdf.build(elements)

    buffer.seek(0)
    return buffer


def generate_stock_order_pdf(logs):
    buffer = io.BytesIO()

    font_path = os.path.join(settings.BASE_DIR, "static/fonts/Vazirmatn-Regular.ttf")
    pdfmetrics.registerFont(TTFont("Vazirmatn", font_path))

    # ایجاد PDF
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    # **۱. ساخت هدر جدول**
    data = [["انجام شد", "وضعیت", "تاریخ", "توضیحات", "نوع", "تعداد", "برند", "نام کالا", "متقاضی"]]
    data = [[fix_persian_text(str(x)) for x in data[0]]]

    # **۲. اضافه کردن داده‌ها از دیتابیس**
    for log in logs:
        data.append([
            fix_persian_text(str("بله")) if log.completed else fix_persian_text(str("خیر")),
            fix_persian_text(str(log.status)),
            datetime2jalali(log.created).strftime("%Y/%m/%d - %H:%M"),
            fix_persian_text(str(log.description)) or fix_persian_text(str("بدون توضیحات")),
            fix_persian_text(str(log.order_type)),
            log.count,
            fix_persian_text(str(log.brand)),
            fix_persian_text(str(log.name)),
            fix_persian_text(str(log.user)),
        ])

    # **۳. ساخت جدول**
    table = Table(data, colWidths=[30, 70, 100, 100, 30, 20, 80, 80, 70])

    # **۴. تنظیم استایل‌های جدول**

    table.setStyle(TABLE_STYLE)

    # **۵. اضافه کردن جدول به PDF**
    elements.append(table)
    pdf.build(elements)

    buffer.seek(0)
    return buffer


def generate_vacation_req_pdf(logs):
    buffer = io.BytesIO()

    font_path = os.path.join(settings.BASE_DIR, "static/fonts/Vazirmatn-Regular.ttf")
    pdfmetrics.registerFont(TTFont("Vazirmatn", font_path))

    # ایجاد PDF
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    # **۱. ساخت هدر جدول**
    headers = ["متقاضی", "جایگزین", "نوع", "شروع", "پایان", "مدت", "توضیحات", "ثبت", "وضعیت"]
    headers.reverse()
    reshaped_headers = [fix_persian_text(h) for h in headers]
    data = [reshaped_headers]

    # **۳. تبدیل داده‌ها به لیست و اصلاح فارسی**
    for log in logs:
        data.append([
            fix_persian_text(str(log.status)),
            fix_persian_text(log.created.strftime("%Y/%m/%d - %H:%M")),
            fix_persian_text(str(log.description) if log.description else "بدون توضیحات"),
            fix_persian_text(str(log.duration)),
            fix_persian_text(log.end_date.strftime("%Y/%m/%d")),
            fix_persian_text(log.start_date.strftime("%Y/%m/%d")),
            fix_persian_text(str(log.type)),
            fix_persian_text(str(log.alternative)),
            fix_persian_text(str(log.user))
        ])

    # **۳. ساخت جدول**
    table = Table(data, colWidths=[60, 100, 100, 20, 60, 60, 30, 70, 70])

    # **۴. تنظیم استایل‌های جدول**

    table.setStyle(TABLE_STYLE)

    # **۵. اضافه کردن جدول به PDF**
    elements.append(table)
    pdf.build(elements)

    buffer.seek(0)
    return buffer


def generate_problem_reps_pdf(logs):
    buffer = io.BytesIO()

    font_path = os.path.join(settings.BASE_DIR, "static/fonts/Vazirmatn-Regular.ttf")
    pdfmetrics.registerFont(TTFont("Vazirmatn", font_path))

    # ایجاد PDF
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    # **۱. ساخت هدر جدول**
    data = [["موثر بوده/نبوده", "تاریخ", "توضیحات", "اقدامات پیشگیری", "اقدامات اصلاحی", "نوع خطا", "اعلام کننده"]]
    data = [[fix_persian_text(str(x)) for x in data[0]]]

    # **۲. اضافه کردن داده‌ها از دیتابیس**
    for log in logs:
        data.append([
            fix_persian_text(str("بله")) if log.effective else fix_persian_text(str("خیر")),
            datetime2jalali(log.created).strftime("%Y/%m/%d - %H:%M"),
            fix_persian_text(str(log.description)) or fix_persian_text(str("بدون توضیحات")),
            fix_persian_text(str(log.prevention_actions)),
            fix_persian_text(str(log.corrective_actions)),
            fix_persian_text(str(log.type)),
            fix_persian_text(str(log.user)),
        ])

    # **۳. ساخت جدول**
    table = Table(data, colWidths=[30, 100, 100, 100, 100, 80, 70])

    # **۴. تنظیم استایل‌های جدول**

    table.setStyle(TABLE_STYLE)

    # **۵. اضافه کردن جدول به PDF**
    elements.append(table)
    pdf.build(elements)

    buffer.seek(0)
    return buffer