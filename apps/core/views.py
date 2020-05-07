from __future__ import unicode_literals

import os

from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from apps.utils.cache import cache_flushdb


def forbidden(request, exception):
    return render(request, "403.html")


def page_not_found(request, exception):
    return render(request, "404.html")


def server_error(request):
    return render(request, "500.html")


def log_view(request, log_name, row_num):
    if request.user.is_superuser:
        log_dir = os.path.join("mainsys/logs")
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
            return render(request, "admin/log.html", context)
        else:
            raise Http404
    else:
        return HttpResponseRedirect("/admin")


@never_cache
def del_cache(request):
    cache_flushdb()
    return HttpResponse('<script>alert("全站缓存清除成功");window.history.back();</script>')


def file_system(request):
    from mainsys.settings import MEDIA_ROOT
    if request.method == "GET":
        file_info_list = []
        file_path = MEDIA_ROOT + request.GET.get("path", "")
        try:
            file_name_list = os.listdir(file_path)
        except FileNotFoundError:
            file_name_list = []
        for file_name in file_name_list:
            file_info_list.append({
                "file_name": file_name,
                "is_dir": os.path.isdir(file_path + "/" + file_name),
                "file_size": os.path.getsize(file_path  + "/" + file_name) // 1024
            })
        return render(request, "admin/files.html", {"file_info_list": file_info_list})
    else:
        method = request.POST.get("method", "del")
        path = MEDIA_ROOT + request.POST.get("path", "")
        if method == "del":  # 删除文件夹或文件
            if os.path.isdir(path):  # 如果是文件夹
                os.removedirs(path)
            else:
                os.unlink(path)
        elif method == "add_file":  # 上传文件
            pass
        elif method == "add_dir":  # 新建文件夹
            os.mkdir(r"E:\zzq_project\gmx\media\test.py")
            pass
        elif method == "rename":
            os.rename(r"E:\zzq_project\gmx\media\test.py", r"E:\zzq_project\gmx\media\test22.py")
            pass
