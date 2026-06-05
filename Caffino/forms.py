
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model,authenticate
import re

class CustomLoginForm(forms.Form):
    phone_number = forms.CharField(label='شماره تلفن')
    password = forms.CharField(widget=forms.PasswordInput, label='رمز عبور')

    def clean(self):
        phone = self.cleaned_data.get('phone_number')
        password = self.cleaned_data.get('password')
        user = authenticate(phone_number=phone, password=password)
        if not user:
            raise forms.ValidationError('شماره تلفن یا رمز عبور نادرست است.')
        self.user = user
        return self.cleaned_data

    def get_user(self):
        return self.user







User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=150, label='نام و نام خانوادگی')
    phone_number = forms.CharField(max_length=15, label='شماره تماس')
    email = forms.EmailField(required=False, label='ایمیل (اختیاری)')
    address = forms.CharField(widget=forms.Textarea, label='آدرس')

    class Meta:
        model = User
        fields = ['full_name', 'phone_number', 'email', 'address', 'password1', 'password2']  # فیلدهای پیش‌فرض
        labels = {
            'full_name': 'نام و نام خانوادگی',
            'phone_number': 'شماره تماس',
            'email': 'ایمیل (اختیاری)',
            'address': 'آدرس',
            'password1': 'رمز عبور',
            'password2': 'تکرار رمز عبور',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError("رمزهای عبور با هم تطابق ندارند.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = self.cleaned_data['full_name']
        user.phone_number = self.cleaned_data['phone_number']
        user.email = self.cleaned_data['email']
        user.address = self.cleaned_data['address']
        user.set_password(self.cleaned_data['password1'])  # توجه به این که 'password1' هست نه 'password'
        if commit:
            user.save()
        return user




class PhoneResetForm(forms.Form):
    phone = forms.CharField(label='شماره موبایل', max_length=11)







class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'phone_number', 'email', 'address']
        labels = {
            'full_name': 'نام و نام خانوادگی',
            'phone_number': 'شماره تماس',
            'email': 'ایمیل',
            'address': 'آدرس',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'










class ChangePasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور جدید")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="تایید رمز عبور")

    def clean_password(self):
        password = self.cleaned_data.get("password")
        
        # بررسی حداقل طول رمز عبور
        if len(password) < 8:
            raise forms.ValidationError("رمز عبور باید حداقل ۸ کاراکتر باشد.")
        
        # بررسی وجود حروف بزرگ
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("رمز عبور باید حداقل یک حرف بزرگ داشته باشد.")
        
        # بررسی وجود حروف کوچک
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("رمز عبور باید حداقل یک حرف کوچک داشته باشد.")
        
        # بررسی وجود عدد
        if not re.search(r'[0-9]', password):
            raise forms.ValidationError("رمز عبور باید حداقل یک عدد داشته باشد.")
        
        # بررسی وجود کاراکتر خاص
        if not re.search(r'[\W_]', password):
            raise forms.ValidationError("رمز عبور باید حداقل یک کاراکتر خاص (مثل !@#$%^&*) داشته باشد.")
        
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("رمز عبور و تایید آن یکسان نیستند.")

        return cleaned_data
