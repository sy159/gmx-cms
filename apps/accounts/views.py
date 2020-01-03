from __future__ import unicode_literals

from django.contrib.auth import (login as auth_login, logout as auth_logout, authenticate)
from django.contrib.auth.models import User
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from apps.utils.access_control import url_required
from apps.utils.cache import *

err_log = logging.getLogger('error_logger')
search_log = logging.getLogger('search_logger')
debug_log = logging.getLogger('debug_logger')


@url_required
def test(request):
    print(cache_set("马哥", "nb", None))
    print(cache_get("马哥"))
    print(cache_del("马哥"))
    print(cache_get("马哥"))
    # err_log.error("error")
    # search_log.info("info")
    # debug_log.info("debug")
    # print(WebSettings.objects.filter(id=1).first())
    return JsonResponse({"code": "200"}, safe=False)


@csrf_exempt
def login(request):
    # 如果已登录，重定向到首页
    if request.user.is_authenticated():
        return redirect("/index/")
    else:
        if request.method == "POST":
            username = request.POST.get("username", "")
            password = request.POST.get("password", "")
            result = {"code": "200", "msg": ""}
            if not username or not password:
                result["code"] = "400"
                result["msg"] = "用户名或密码不能为空"
                return JsonResponse(result)
            user = authenticate(username=username, password=password)
            if user:
                auth_login(request, user)
                return redirect("/index/")
            else:
                result["code"] = "400"
                result["msg"] = "用户名或密码错误"
                return JsonResponse(result)
        else:
            return render(request, "index.html")


def logout(request):
    auth_logout(request)
    return redirect("/accounts/login/")


@csrf_exempt
@url_required
def set_pwd(request):
    username = request.POST.get("username")
    new_password = request.POST.get("new_password")
    result = {"code": "200", "msg": ""}
    if username and new_password:
        user = User.objects.filter(username=username).first()
        if user:
            user.set_password(password=new_password)
            return JsonResponse(result)
    result["code"] = "400"
    result["msg"] = "密码修改失败"
    return JsonResponse(result)


@csrf_exempt
def signup(request):
    # 如果已登录，重定向到首页
    if request.user.is_authenticated():
        return redirect("/index/")
    else:
        if request.method == "POST":
            username = request.POST.get("username", "")
            password = request.POST.get("password", "")
            result = {"code": "200", "msg": ""}
            if not username or not password:
                result["code"] = "400"
                result["msg"] = "用户名或密码不能为空"
                return JsonResponse(result)
            if User.objects.filter(username=username).exists():
                result["code"] = "400"
                result["msg"] = "该用户名已存在"
                return JsonResponse(result)
            user = User.objects.create_user(username=username, password=password)
            return JsonResponse(result)
        else:
            return render(request, "index.html")
