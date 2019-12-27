from __future__ import unicode_literals

import time

from apps.utils.cryption import aes_encrypt


def get_sign(user: str, pwd: str) -> str:
    return aes_encrypt.encrypt("%s|%s|%s" % (user, pwd, str(time.time())))


# 扩展login_required装饰器(判断用户是否登录)
def url_required(func):
    def wrapper(*args, **kwargs):
        from django.http import HttpResponseBadRequest
        from django.http import HttpResponseRedirect
        request = args[0]
        if request.user.is_authenticated():
            return func(*args, **kwargs)
        # 未登录需要验证签名
        sign = request.GET.get('sign', '')
        if not sign:
            return HttpResponseRedirect("/accounts/login/")
        try:
            sign = aes_encrypt.decrypt(sign)
            user, pwd, mtime = sign.split('|')
        except Exception as e:
            return HttpResponseBadRequest("403")
        else:
            # sign5分钟内有效
            if time.time() - float(mtime) <= 60 * 30:
                from django.contrib.auth import authenticate
                user = authenticate(username=user, password=pwd)
                if user:
                    request.user = user
                    return func(*args, **kwargs)

        return HttpResponseBadRequest("403")

    return wrapper
