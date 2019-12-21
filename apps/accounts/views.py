from django.shortcuts import render
from django.http.response import JsonResponse
from apps.utils.cache import *

import logging
err_log = logging.getLogger('error_logger')
search_log = logging.getLogger('search_logger')
debug_log = logging.getLogger('debug_logger')
from django.views.decorators.cache import never_cache
from apps.accounts.models import UserInfo
# Create your views here.
from django.contrib.auth.decorators import login_required

@never_cache
def test(request):
    # print(request.path)
    # print(cache_set("马哥","nb", None))
    # print(cache_get("马哥"))
    # print(cache_del("马哥"))
    # print(cache_get("马哥"))
    err_log.error("error")
    search_log.info("info")
    debug_log.info("debug")

    raise SyntaxError
    return JsonResponse({"code": "200"}, safe=False)
