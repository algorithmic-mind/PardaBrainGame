from django import template
import jdatetime
from datetime import datetime

register = template.Library()

@register.filter
def format_duration(seconds):
    """
    تبدیل ثانیه به فرمت دقیقه و ثانیه
    اگر کمتر از 60 ثانیه باشد، فقط ثانیه نمایش داده می‌شود
    """
    try:
        seconds = int(float(seconds))
        if seconds < 60:
            return f"{seconds} ثانیه"
        else:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes} دقیقه و {remaining_seconds} ثانیه"
    except (ValueError, TypeError):
        return "0 ثانیه"

@register.filter
def jalali_date(value, format_string="%Y/%m/%d"):
    """
    تبدیل تاریخ میلادی به شمسی
    
    نمونه استفاده:
    {{ your_date|jalali_date }}  # فرمت پیش‌فرض: 1402/01/01
    {{ your_date|jalali_date:"%Y/%m/%d %H:%M" }}  # فرمت سفارشی: 1402/01/01 14:30
    """
    if not value:
        return ""
    
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                value = datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                return value
    
    jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
    
    # تبدیل اعداد انگلیسی به فارسی
    persian_numbers = {
        '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
        '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
    }
    
    result = jalali_date.strftime(format_string)
    for en, fa in persian_numbers.items():
        result = result.replace(en, fa)
    
    # تبدیل نام ماه‌ها به فارسی (اگر در فرمت وجود داشته باشد)
    persian_months = {
        'Farvardin': 'فروردین', 'Ordibehesht': 'اردیبهشت', 'Khordad': 'خرداد',
        'Tir': 'تیر', 'Mordad': 'مرداد', 'Shahrivar': 'شهریور',
        'Mehr': 'مهر', 'Aban': 'آبان', 'Azar': 'آذر',
        'Dey': 'دی', 'Bahman': 'بهمن', 'Esfand': 'اسفند'
    }
    
    for en, fa in persian_months.items():
        result = result.replace(en, fa)
    
    return result

@register.filter
def jalali_date_with_text(value, format_string=None):
    """
    تبدیل تاریخ میلادی به شمسی با فرمت متنی
    
    نمونه استفاده:
    {{ your_date|jalali_date_with_text }}  # خروجی: ۱۲ مهر ۱۴۰۲
    """
    if not value:
        return ""
    
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                value = datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                return value
    
    jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
    
    # نام ماه‌های فارسی
    persian_months = [
        'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
        'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
    ]
    
    # تبدیل اعداد انگلیسی به فارسی
    persian_numbers = {
        '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
        '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
    }
    
    day = str(jalali_date.day)
    month = persian_months[jalali_date.month - 1]
    year = str(jalali_date.year)
    
    # تبدیل اعداد به فارسی
    for en, fa in persian_numbers.items():
        day = day.replace(en, fa)
        year = year.replace(en, fa)
    
    if format_string == "with_time":
        hour = str(jalali_date.hour)
        minute = str(jalali_date.minute)
        
        # تبدیل اعداد ساعت و دقیقه به فارسی
        for en, fa in persian_numbers.items():
            hour = hour.replace(en, fa)
            minute = minute.replace(en, fa)
        
        return f"{day} {month} {year} - ساعت {hour}:{minute}"
    
    return f"{day} {month} {year}"