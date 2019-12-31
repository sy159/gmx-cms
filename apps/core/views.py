from __future__ import unicode_literals

import os

from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from apps.utils.cache import cache_flushdb
from mainsys.settings import PROJECT_DIRNAME


def log_view(request, log_name, row_num):
    if request.user.is_superuser:
        log_dir = os.path.join(PROJECT_DIRNAME, "../mainsys/logs/")
        log_file = os.path.join(log_dir, log_name)
        if os.path.isfile(log_file):
            log_file_handle = open(log_file, 'r')
            row_num = int(row_num)
            flines = log_file_handle.readlines()
            lines = []
            count = 0
            for line in reversed(flines):
                lines.append(line.rstrip())
                count += 1
                if count >= row_num:
                    break
            log_file_handle.close()

            # 遍历log目录下所有log文件
            all_logs = []
            for each_log in os.listdir(log_dir):
                if each_log != "index.html" and os.path.isfile(os.path.join(log_dir, each_log)):
                    all_logs.append(each_log)
            context = {"lines": reversed(lines), "log_name": log_name, "all_logs": all_logs}
            return render(request, "admin/../../templates/log.html", context)
        else:
            raise Http404
    else:
        return HttpResponseRedirect("/admin")


@never_cache
def delcache(request):
    cache_flushdb()
    return HttpResponse('<script>alert("全站缓存清除成功");window.history.back();</script>')
