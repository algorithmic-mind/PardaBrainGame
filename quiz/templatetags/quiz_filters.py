from django import template
import jdatetime
from datetime import datetime

register = template.Library()

from django.utils.timezone import is_aware, make_naive
import pytz

@register.filter
def jalali_date(value, format_string="%Y/%m/%d"):
    """
    تبدیل datetime میلادی (با یا بدون timezone) به تاریخ شمسی با فرمت انتخابی.
    """
    if not value:
        return ""

    try:
        # اگر مقدار aware باشد، به منطقه زمانی تهران تبدیلش می‌کنیم
        if is_aware(value):
            tehran_tz = pytz.timezone('Asia/Tehran')
            value = value.astimezone(tehran_tz)
        else:
            # اگر USE_TZ فعال است ولی datetime naive است، فرض بر این می‌گذاریم که زمان UTC است
            if settings.USE_TZ:
                tehran_tz = pytz.timezone('Asia/Tehran')
                value = tehran_tz.localize(value)

        # تبدیل به تاریخ شمسی
        jalali_dt = jdatetime.datetime.fromgregorian(datetime=value)
        result = jalali_dt.strftime(format_string)

        # تبدیل اعداد انگلیسی به فارسی
        persian_numbers = {
            '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
            '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
        }
        for en, fa in persian_numbers.items():
            result = result.replace(en, fa)

        return result
    except Exception as e:
        return str(value)  # در صورت خطا، همان مقدار اولیه را برمی‌گرداند


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