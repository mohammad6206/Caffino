# Python built-in
import random
import requests

# Django imports
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Avg
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

# Local app imports
from Caffino.models import (
    Product, Cart, CartItem, Rating, SMSVerification, Order,
    OrderItem, Payment, Favorite, Coupon, ContactMessage,
    Comment, BannerImage, Category
)
from Caffino.forms import (
    CustomUserCreationForm, CustomLoginForm,
    ProfileEditForm, PhoneResetForm, ChangePasswordForm
)
from .templatetags.custom_filters import detailed_rating




# ----------------- Views -----------------
def index_view(request):
    banner_images = BannerImage.objects.filter(is_active=True).order_by('order')
    latest_products = Product.objects.all().order_by('-created_at')[:3]
    
    # تغییر این بخش:
    testimonials = ContactMessage.objects.all().order_by('-created_at')[:5]
    
    context = {
        'banner_images': banner_images,
        'latest_products': latest_products,
        'testimonials': testimonials,
    }
    return render(request, 'index.html', context)




def submit_contact(request):
    if request.method == 'POST':
        # پاک کردن پیام‌های قبلی
        storage = messages.get_messages(request)
        for _ in storage:
            pass
        
        # اعتبارسنجی داده‌ها
        required_fields = ['name', 'email', 'subject', 'message']
        if not all(request.POST.get(field) for field in required_fields):
            messages.error(request, 'لطفاً تمام فیلدهای ضروری را پر کنید')
            return redirect('Caffino:contact')
        
        try:
            ContactMessage.objects.create(
                name=request.POST['name'],
                email=request.POST['email'],
                subject=request.POST['subject'],
                message=request.POST['message'],
                user=request.user if request.user.is_authenticated else None,
                is_approved=False
            )
            messages.success(request, 'نظر شما با موفقیت ثبت شد و پس از تأیید نمایش داده خواهد شد')
            return redirect('Caffino:contact')  # تغییر مسیر به صفحه تماس
            
        except Exception as e:
            messages.error(request, f'خطا در ثبت نظر: {str(e)}')
            return redirect('Caffino:contact')
    
    return redirect('Caffino:contact')

def About_view(request):
    return render(request, 'About.html')

def Contact_view(request):
    testimonials = ContactMessage.objects.all().order_by('-created_at')[:5]
    context = {

        'testimonials': testimonials

    }
    return render(request, 'Contact.html',context)

def product_view(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'gallery.html', {'products': products, 'categories': categories})

def services_view(request):
    return render(request, 'services.html')


@login_required
def cart_view(request):
    try:
        cart = request.user.cart
        cart_items = CartItem.objects.filter(cart=cart).select_related('product')
        
        total_items = sum(item.quantity for item in cart_items)
        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        grand_total = subtotal
        
    except Cart.DoesNotExist:
        cart_items = []
        total_items = 0
        subtotal = 0
        grand_total = 0

    context = {
        'cart_items': cart_items,
        'total_items': total_items,
        'subtotal': subtotal,
        'grand_total': grand_total,
    }
    return render(request, 'cart.html', context)



@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, pk=product_id)

        try:
            user_cart = request.user.cart
        except Cart.DoesNotExist:
            user_cart = Cart.objects.create(user=request.user)

        cart_item, item_created = CartItem.objects.get_or_create(cart=user_cart, product=product)

        if not item_created:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item.quantity = quantity  # اگر آیتم جدید است، تعداد را تنظیم کنید
            cart_item.save()

        messages.success(request, f"تعداد {quantity} عدد از محصول {product.name} به سبد خرید شما اضافه شد")
    return redirect('Caffino:product_detail', product_id=product_id)





def product_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # محصولات مرتبط
    related_products = Product.objects.filter(
        Q(category=product.category)
    ).exclude(
        id=product.id
    ).distinct().order_by('?')[:10]

    # دریافت نظرات محصول
    ratings = Rating.objects.filter(product=product).order_by('-created_at')
    total_ratings = ratings.count()

    # بررسی علاقه‌مندی
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(
            user=request.user,
            product=product
        ).exists()

    # محاسبه ستاره‌ها با استفاده از فیلتر `detailed_rating`
    stars = detailed_rating(product.average_rating or 0)

    context = {
        'product': product,
        'related_products': related_products,
        'is_favorite': is_favorite,
        'ratings': ratings,
        'total_ratings': total_ratings,
        'stars': stars,  # لیست وضعیت ستاره‌ها به قالب ارسال میشه
    }

    return render(request, 'product_detail.html', context)



@login_required
def submit_rating(request, product_id):
    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        comment = request.POST.get('comment')
        product = get_object_or_404(Product, pk=product_id)

        Rating.objects.create(
            user=request.user,
            product=product,
            rating=rating_value,
            comment=comment
        )
        messages.success(request, "نظر شما با موفقیت ثبت شد.")
        return redirect('Caffino:product_detail', product_id=product_id)
    return redirect('Caffino:product_detail', product_id=product_id)

# ----------------- User Authentication -----------------

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'ثبت‌نام با موفقیت انجام شد.')
            return redirect('Caffino:login')  # مسیر لاگین شما
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})




def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next')

    # اگر کاربر لاگین کرده باشه، مستقیم به ایندکس بره
    if request.user.is_authenticated:
        return redirect('Caffino:index')

    # اگر از طریق برگشت مرورگر اومده ولی لاگین نیست و next داره
    if not request.user.is_authenticated and next_url and not next_url.startswith('/'):
        return redirect('Caffino:index')

    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # ریدایرکت به next معتبر یا ایندکس
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            else:
                return redirect('Caffino:index')
        else:
            messages.success(request, "شماره تلفن یا رمز عبور اشتباه است.")
    else:
        form = CustomLoginForm()

    return render(request, 'login.html', {
        'form': form,
        'next': next_url or '',
    })







@login_required
def dashboard(request):
    # تاریخ امروز برای فیلتر کوپن‌ها
    now = timezone.now()
    
    context = {
        # سفارش‌های اخیر کاربر
        'orders': Order.objects.filter(user=request.user).order_by('-created_at')[:6],
        
        # محصولات خریداری شده
        'purchased_items': OrderItem.objects.filter(
            order__user=request.user
        ).select_related('product', 'order').order_by('-order__created_at')[:3],
        
        # محصولات مورد علاقه
        'favorites': Favorite.objects.filter(
            user=request.user
        ).select_related('product').order_by('-created_at')[:3],
        
        # کوپن‌های فعال (با توجه به مدل شما)
        'coupons': Coupon.objects.filter(
            valid_from__lte=now,
            valid_to__gte=now,
            is_active=True
        ),
        
        # پیام‌های ارسالی به پشتیبانی
        'support_messages': ContactMessage.objects.filter(
            user=request.user
        ).order_by('-created_at'),
        
        # نظرات کاربر روی محصولات
        'product_comments': Comment.objects.filter(
            user=request.user
        ).select_related('product').order_by('-created_at'),
    }
    return render(request, 'dashboard.html', context)





def logout_view(request):
    logout(request)
    return redirect('Caffino:login')



# views.py

def send_sms_code(phone_number, code):
    api_key = 'YOUR_API_KEY'
    url = 'https://api.sms.ir/v1/send/verify'
    payload = {
        "mobile": phone_number,
        "templateId": YOUR_TEMPLATE_ID,
        "parameters": [
            {"name": "Code", "value": code}
        ]
    }
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': api_key
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code == 200




def request_reset_code(request):
    if request.method == 'POST':
        form = PhoneResetForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            code = str(random.randint(100000, 999999))
            SMSVerification.objects.create(phone_number=phone, code=code)
            send_sms_code(phone, code)
            request.session['reset_phone'] = phone  # ذخیره شماره برای مراحل بعدی
            return redirect('verify_code')
    else:
        form = PhoneResetForm()
    
    return render(request, 'request_reset_code.html', {'form': form})






def verify_code(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        code = request.POST.get('code')
        try:
            record = SMSVerification.objects.get(phone_number=phone, code=code)
            if record.is_valid():
                # هدایت به صفحه تغییر رمز عبور
                return redirect('set_new_password', phone=phone)
            else:
                messages.error(request, "کد منقضی شده است.")
        except SMSVerification.DoesNotExist:
            messages.error(request, "کد نامعتبر است.")
    return render(request, 'verify_code.html')










def set_new_password(request, phone):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['password']
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, "رمز عبور با موفقیت تغییر یافت")
            return render('Caffino:login')
    else:
        form = ChangePasswordForm()

    return render(request, 'set_new_password.html', {'form': form})





# accounts/views.py

@login_required
def edit_profile(request):
    profile = request.user

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('Caffino:dashboard')  # یا مسیر مناسب شما
    else:
        form = ProfileEditForm(instance=profile)

    return render(request, 'edit_profile.html', {'form': form})







def update_cart_item(request, item_id):
    if request.method == 'POST':
        try:
            cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
            quantity = int(request.POST.get('quantity', 1))
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, f"تعداد {cart_item.product.name} به {quantity} عدد به‌روزرسانی شد.")
            else:
                cart_item.delete()
                messages.info(request, f"{cart_item.product.name} از سبد خرید حذف شد.")
            return redirect('Caffino:cart')
        except CartItem.DoesNotExist:
            messages.error(request, "آیتم مورد نظر در سبد خرید شما یافت نشد.")
            return redirect('Caffino:cart')
        except ValueError:
            messages.error(request, "تعداد وارد شده نامعتبر است.")
            return redirect('Caffino:cart')
    return redirect('Caffino:cart') # اگر متد POST نباشد










def remove_from_cart(request, item_id):
    if request.method == 'POST':
        try:
            cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
            cart_item.delete()
            messages.info(request, f"{cart_item.product.name} از سبد خرید شما حذف شد.")
        except CartItem.DoesNotExist:
            messages.error(request, "آیتم مورد نظر در سبد خرید شما یافت نشد.")
        return redirect('Caffino:cart')
    return redirect('Caffino:cart') # اگر متد POST نباشد

















@login_required
def process_payment(request):
    # 1. ایجاد سفارش از سبد خرید
    try:
        cart = request.user.cart
        cart_items = cart.items.all()
        
        if not cart_items.exists():
            messages.error(request, "سبد خرید شما خالی است")
            return redirect('Caffino:cart')
        
        # محاسبه مبلغ کل
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        
        # ایجاد سفارش
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            status='pending'
        )
        
        # ایجاد آیتم‌های سفارش
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
        
        # 2. ایجاد رکورد پرداخت
        payment = Payment.objects.create(
            order=order,
            payment_method='درگاه پرداخت',  # یا روش پرداخت انتخابی کاربر
            is_paid=False
        )
        
        # 3. در اینجا باید به درگاه پرداخت متصل شوید
        # برای نمونه، ما پرداخت را موفق فرض می‌کنیم:
        payment.is_paid = True
        payment.paid_at = timezone.now()
        payment.save()
        
        # 4. به‌روزرسانی وضعیت سفارش
        order.status = 'paid'
        order.save()
        
        # 5. خالی کردن سبد خرید
        cart_items.delete()
        
        # 6. هدایت به صفحه موفقیت‌آمیز
        return redirect(reverse('Caffino:payment_success') + f'?order_code={order.order_code}')
        
    except Exception as e:
        messages.error(request, f"خطا در پرداخت: {str(e)}")
        return redirect('payment_failed')
    




@login_required
def payment_success(request):
    order_code = request.GET.get('order_code')
    try:
        order = Order.objects.get(order_code=order_code, user=request.user)
        return render(request, 'success.html', {
            'order': order,
            'payment': order.payment
        })
    except Order.DoesNotExist:
        messages.error(request, "سفارش یافت نشد")
        return redirect('home')
    
    



@login_required
def payment_failed(request):
    # دریافت پیام خطا از session یا پارامتر GET
    error_message = request.GET.get('error', 'پرداخت با خطا مواجه شد. لطفا مجددا تلاش کنید.')
    
    # نمایش پیام به کاربر
    messages.error(request, error_message)
    
    context = {
        'error_message': error_message,
        'order_code': request.GET.get('order_code'),
    }
    return render(request, 'failed.html', context)








@login_required
def order_detail(request, order_code):
    order = get_object_or_404(Order, order_code=order_code, user=request.user)
    order_items = order.items.all()
    
    context = {
        'order': order,
        'items': order_items,
        'title': f'جزئیات سفارش #{order.order_code}'
    }
    return render(request, 'order_detail.html', context)





@login_required
def add_to_favorites(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Favorite.objects.get_or_create(user=request.user, product=product)
    messages.success(request, "محصول به علاقه‌مندی‌ها اضافه شد")
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def remove_from_favorites(request, product_id):
    Favorite.objects.filter(user=request.user, product_id=product_id).delete()
    messages.success(request, "محصول از علاقه‌مندی‌ها حذف شد")
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(
        user=request.user
    ).select_related('product')
    return render(request, 'list.html', {'favorites': favorites})





@login_required
def coupons(request):
    now = timezone.now()
    coupons = Coupon.objects.filter(
        valid_from__lte=now,
        valid_to__gte=now,
        is_active=True
    ).order_by('-valid_to')  # نمایش جدیدترین کوپن‌ها اول
    context = {
        'coupons': coupons,
    }
    return render(request, 'coupons.html', context)







@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'order_history.html', context)










@login_required
def purchased_products_list(request):
    # فقط سفارش‌هایی که پرداخت شده‌ان رو در نظر می‌گیریم
    order_items = OrderItem.objects.filter(
        order__user=request.user,
        order__status='paid'  # یا status دلخواه مثل 'paid'
    ).select_related('product').order_by('-order__created_at')

    context = {
        'order_items': order_items
    }
    return render(request, 'purchased_products.html', context)









def product_filter(request):
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')

    products = Product.objects.all()

    if search_query:
        products = products.filter(name__icontains=search_query)

    if category_id:
        products = products.filter(category_id=category_id)

    html = render_to_string('product_list_partial.html', {'products': products})
    return HttpResponse(html)
