from django.urls import path
from Caffino.views import (
    index_view, About_view, Contact_view, product_view, services_view,
    cart_view, product_detail_view, add_to_cart, submit_rating,register,
    dashboard,request_reset_code,verify_code,set_new_password,
    edit_profile,logout_view,update_cart_item,remove_from_cart
    ,payment_success,process_payment,payment_failed,order_detail 
    ,favorites_list,add_to_favorites,remove_from_favorites,coupons,order_history,
    submit_contact,purchased_products_list,product_filter  
)
from Caffino.views import login_view    


app_name = 'Caffino'

urlpatterns = [
    path("", index_view, name='index'),
    path("about", About_view, name='about'),
    path("contact", Contact_view, name='contact'),
    path("products", product_view, name='products'),   
    path("services", services_view, name='services'),
    path("cart", cart_view, name='cart'),
    path("product/<int:product_id>/", product_detail_view, name='product_detail'),
    path("add-to-cart/<int:product_id>/", add_to_cart, name='add_to_cart'),
     path('update-cart-item/<int:item_id>/',update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:item_id>/',remove_from_cart, name='remove_from_cart'),
    path("product/<int:product_id>/submit-rating/", submit_rating, name='submit_rating'),
    path('submit-contact/', submit_contact, name='submit_contact'),
    path("register/",register, name='register'),
    path("login/", login_view, name='login'),
    path("logout/",logout_view, name='logout'),  
    path('dashboard/',dashboard, name='dashboard'),
    path('password-reset/', request_reset_code, name='phone_reset'),
    path('verify-code/', verify_code, name='verify_code'),
    path('set-password/<str:phone>/', set_new_password, name='set_new_password'),
    path('edit-profile/',edit_profile, name='edit_profile'),
    path('checkout/process/', process_payment, name='process_payment'),
    path('payment/success/', payment_success, name='payment_success'),
    path('payment/failed/', payment_failed, name='payment_failed'),
    path('orders/<uuid:order_code>/', order_detail, name='order_detail'),
    path('favorites/', favorites_list, name='favorites_list'),
    path('favorites/add/<int:product_id>/', add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<int:product_id>/', remove_from_favorites, name='remove_from_favorites'),
    path('accounts/coupons/',coupons, name='coupons'),
    path('orders/history/', order_history, name='order_history'),
    path('purchased-products/', purchased_products_list, name='purchased_products'),
    path('products/filter/',product_filter, name='product_filter'),



]