from django.contrib import messages
from django.conf import settings

class AutoDismissMessagesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        if hasattr(request, '_messages'):
            storage = messages.get_messages(request)
            for message in storage:
                # اضافه کردن کلاس خودکار به تمام پیام‌ها
                if not message.extra_tags:
                    message.extra_tags = 'auto-dismiss'
                elif 'auto-dismiss' not in message.extra_tags:
                    message.extra_tags += ' auto-dismiss'
        return response
    





from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect

class NoCacheMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
