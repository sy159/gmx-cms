from __future__ import unicode_literals

from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from mainsys.webconfig import site_conf


@require_GET
@never_cache
def home(request):
    redirect_url = site_conf[request.get_host()].get("home_url")
    if redirect_url:
        return HttpResponseRedirect(redirect_url)
    theme = site_conf[request.get_host()].get("system_theme", "default")
    return render(request, f"fethemes/{theme}/index.html", {})


@require_GET
@never_cache
def index(request, page):
    theme = site_conf[request.get_host()].get("system_theme", "default")
    return render(request, f"fethemes/{theme}/{page}.html")


def test(request):
    return JsonResponse({"lala": "asdfa"})
