from __future__ import unicode_literals

import hashlib

from django.shortcuts import render

try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object  # Django 1.4.x - Django 1.9.x
from django.core.cache import cache


class RequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        url_list = ["/accounts/test/"]  # 需要做访问频率限制的url
        black_ip = []
        if request.path in url_list:
            if request.META.get('HTTP_X_FORWARDED_FOR'):
                ip = request.META['HTTP_X_FORWARDED_FOR']
            else:
                ip = request.META['REMOTE_ADDR']
            if ip in black_ip:
                return render(request, '403.html')
            cache_key = hashlib.md5(ip.encode("utf-8")).hexdigest()
            ip_count = cache.get(cache_key)
            if ip_count:
                if ip_count >= 300:
                    return render(request, "429.html")
                else:
                    try:
                        cache.incr(cache_key)
                    except ValueError:
                        pass
            else:
                cache.set(cache_key, 1, 60 * 30)

    def process_response(self, request, response):
        if response.status_code >= 500:
            res = response.content.decode("utf-8")
        return response
