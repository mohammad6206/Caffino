from jalali_date.admin import ModelAdminJalaliMixin
from jalali_date import datetime2jalali
from django.contrib import admin
from .models import ( 
    Product, Category, Order,
    OrderItem, Payment, Cart, CartItem, Comment,
    ContactMessage, Coupon, User, BannerImage
)

@admin.register(BannerImage)
class BannerImageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    ordering = ('order',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'weight', 'created_at', 'updated_at']
    search_fields = ['name', 'category__name']
    list_filter = ['category', 'is_active']


@admin.register(Order)
class OrderAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ['order_code', 'user', 'total_price', 'status', 'get_jalali_date']
    search_fields = ['order_code', 'user__full_name']
    list_filter = ['status']

    def get_jalali_date(self, obj):
        return datetime2jalali(obj.created_at).strftime("%Y/%m/%d")
    get_jalali_date.short_description = 'تاریخ ثبت (شمسی)'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'get_jalali_date']
    search_fields = ['product__name', 'user__full_name']

    def get_jalali_date(self, obj):
        return datetime2jalali(obj.created_at).strftime("%Y/%m/%d")
    get_jalali_date.short_description = 'تاریخ ثبت (شمسی)'

@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_approved', 'get_jalali_date']
    list_editable = ['is_approved']
    list_filter = ['is_approved']
    search_fields = ['name', 'email', 'subject']
    
    def get_jalali_date(self, obj):
        return datetime2jalali(obj.created_at).strftime("%Y/%m/%d")
    get_jalali_date.short_description = 'تاریخ ثبت (شمسی)'


admin.site.register(Category)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Coupon)
admin.site.register(User)
