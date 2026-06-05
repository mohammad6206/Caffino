from django import template
import math

register = template.Library()

@register.filter
def detailed_rating(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0

    # گرد کردن به بالا
    rounded = math.ceil(value)
    
    # ساخت لیست ستاره‌ها
    stars = []
    for i in range(1, 6):
        if i <= rounded:
            stars.append('full')
        else:
            stars.append('empty')
    return stars
