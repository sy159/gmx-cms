from __future__ import unicode_literals

import hashlib

from django.shortcuts import render

try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object  # Django 1.4.x - Django 1.9.x
from django.core.cache import cache
from django.conf import settings
from mainsys.settings import MIDDLEWARE


class RequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        url_list = ["/accounts/test/"]  # 需要做访问频率限制的url
        black_ip = []  # ip黑名单
        # 如果sign放在header里面的话(header key必须增加前缀HTTP，同时大写)
        header_sign = request.META.get("HTTP_SIGN", "")
        if request.path in url_list:
            if request.META.get('HTTP_X_FORWARDED_FOR'):
                ip = request.META.get('HTTP_X_FORWARDED_FOR', "").split(',')[0]  # 真实的ip
            else:
                ip = request.META.get('REMOTE_ADDR')  # 代理ip
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


class XFrameOptionsMiddleware(MiddlewareMixin):
    """
    Set the X-Frame-Options HTTP header in HTTP responses.

    Do not set the header if it's already set or if the response contains
    a xframe_options_exempt value set to True.

    By default, set the X-Frame-Options header to 'SAMEORIGIN', meaning the
    response can only be loaded on a frame within the same site. To prevent the
    response from being loaded in a frame in any site, set X_FRAME_OPTIONS in
    your project's Django settings to 'DENY'.
    """
    def process_response(self, request, response):
        # Don't set it if it's already in the response
        if response.get('X-Frame-Options') is not None and "simpleui.middlewares.SimpleMiddleware" not in MIDDLEWARE:
            return response

        # Don't set it if they used @xframe_options_exempt
        if getattr(response, 'xframe_options_exempt', False):
            return response

        response['X-Frame-Options'] = self.get_xframe_options_value(request,
                                                                    response)
        print(response["X-Frame-Options"])
        return response

    def get_xframe_options_value(self, request, response):
        """
        Get the value to set for the X_FRAME_OPTIONS header. Use the value from
        the X_FRAME_OPTIONS setting, or 'DENY' if not set.

        This method can be overridden if needed, allowing it to vary based on
        the request or response.
        """
        return getattr(settings, 'X_FRAME_OPTIONS', 'DENY').upper()
