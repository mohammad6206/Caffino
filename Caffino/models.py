from django.db.models import Avg
import cv2
import numpy as np
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from django.core.files.base import ContentFile
import os
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
from CafiinoShop import settings
from django.db import models

# 1. Category Model
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 2. Product Model
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.IntegerField(verbose_name="قیمت (تومان)")
    image = models.ImageField(upload_to='products/')
    weight = models.PositiveIntegerField()  
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return self.name
    
    @property
    def average_rating(self):
        result = self.ratings.aggregate(avg=Avg('rating'))
        return result['avg'] or 0

# 3. Order Model
class Order(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='orders')
    order_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    total_price = models.IntegerField(verbose_name="قیمت (تومان)")
    status_choices = [
    ('pending', 'در انتظار پرداخت'),
    ('paid', 'پرداخت شده'),
    ('shipped', 'ارسال شده'),
    ('delivered', 'تحویل داده شده'),
    ('canceled', 'لغو شده'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

# 4. OrderItem Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.IntegerField(verbose_name="قیمت (تومان)")

    @property
    def total_price(self):
        return self.price * self.quantity

# 5. Payment Model
class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=50)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

# 6. Cart Model
class Cart(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

# 7. CartItem Model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    @property
    def total_price(self):
        return self.product.price * self.quantity

# 8. Comment Model
class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

# 9. ContactMessage Model
class ContactMessage(models.Model):
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False, verbose_name="تأیید شده")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

# 10. Coupon Model
class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.PositiveIntegerField()
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code




class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='کاربر'
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='محصول'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )

    class Meta:
        verbose_name = 'علاقه‌مندی'
        verbose_name_plural = 'علاقه‌مندی‌ها'
        unique_together = ('user', 'product')  # جلوگیری از تکرار

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
# User Model (Custom)



class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, full_name, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('شماره تلفن الزامی است')
        user = self.model(phone_number=phone_number, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, full_name, password=None, email=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not username:
            raise ValueError('نام کاربری الزامی است')
        user = self.model(username=username, full_name=full_name, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=15, unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)  # افزودن default
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'  # تنظیم USERNAME_FIELD به 'username'
    REQUIRED_FIELDS = ['full_name', 'phone_number'] # نگه داشتن phone_number در REQUIRED_FIELDS برای create_user

    def __str__(self):
        return self.phone_number




class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(choices=[(1, '1 ستاره'), (2, '2 ستاره'), (3, '3 ستاره'), (4, '4 ستاره'), (5, '5 ستاره')])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def stars_display(self):
        return '⭐' * self.rating
    stars_display.short_description = 'امتیاز'
    
    class Meta:
        verbose_name = 'امتیاز'
        verbose_name_plural = 'امتیازات'

    def __str__(self):
        return f"امتیاز {self.rating} توسط {self.user.username} برای {self.product.name}"









# models.py

class SMSVerification(models.Model):
    phone_number = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() - self.created_at < timezone.timedelta(minutes=5)







class BannerImage(models.Model):
    image = models.ImageField(upload_to='banners/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    def save(self, *args, **kwargs):
        # ابتدا ذخیره اولیه
        super().save(*args, **kwargs)
        
        # ابعاد مورد نظر (همانند CSS)
        TARGET_WIDTH = 2000
        TARGET_HEIGHT = 450
        
        # پردازش تصویر
        img_path = self.image.path
        img = cv2.imread(img_path)
        
        if img is not None:
            # تغییر سایز با حفظ نسبت ابعاد و برش به اندازه دقیق
            h, w = img.shape[:2]
            
            # محاسبه نسبت جدید
            target_ratio = TARGET_WIDTH / TARGET_HEIGHT
            img_ratio = w / h
            
            if img_ratio > target_ratio:
                # تصویر عریض‌تر است
                new_height = TARGET_HEIGHT
                new_width = int(new_height * img_ratio)
            else:
                # تصویر بلندتر است
                new_width = TARGET_WIDTH
                new_height = int(new_width / img_ratio)
            
            # تغییر سایز
            resized = cv2.resize(img, (new_width, new_height))
            
            # برش به اندازه دقیق
            start_x = max(0, (new_width - TARGET_WIDTH) // 2)
            start_y = max(0, (new_height - TARGET_HEIGHT) // 2)
            cropped = resized[start_y:start_y+TARGET_HEIGHT, start_x:start_x+TARGET_WIDTH]
            
            # ذخیره تصویر پردازش شده
            _, buffer = cv2.imencode('.jpg', cropped)
            io_buf = BytesIO(buffer)
            
            # ذخیره فایل جدید
            file_name = os.path.basename(self.image.name)
            self.image.save(
                file_name,
                ContentFile(io_buf.getvalue()),
                save=False
            )
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.alt_text or f"Banner {self.id}"