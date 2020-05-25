from __future__ import unicode_literals

import os
import time

from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

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


@csrf_exempt
def file_system(request):
    if request.user.is_superuser:
        from mainsys.settings import MEDIA_ROOT
        if request.method == "GET":
            return render(request, "admin/file_system.html")
        else:
            method = request.POST.get("method", "get")
            path = MEDIA_ROOT + request.POST.get("path", "")
            result = {"code": "200", "success": True, "msg": ""}
            if method != "add_dir" and not os.path.exists(path):
                result["success"] = False
                result["msg"] = "该文件或者目录不存在"
                return JsonResponse(result, safe=False)
            if method == "del":  # 删除文件夹或文件
                try:
                    if path == "/":  # 删除跟目录
                        raise OSError("根目录不允许删除")
                    if os.path.isdir(path):  # 如果是文件夹
                        import shutil
                        shutil.rmtree(path=path)  # 递归删除文件夹
                        # os.removedirs(path)  # 删除文件夹，如果子级有不为空，就会OSError异常
                    else:
                        os.unlink(path)
                except OSError:
                    result["msg"] = "文件或目录删除失败"
                    result["success"] = False
            elif method == "upload_file":  # 上传文件
                # wl_files = request.FILES.getlist("files", None)  # 多文件上传
                wl_file = request.FILES.get("file", None)
                if not os.path.isdir(path):
                    result["success"] = False
                    result["msg"] = "该目录不存在"
                all_files = filter(lambda files: os.path.isfile(f"{path}/{files}"), os.listdir(path))
                if wl_file.name in all_files:  # 重名
                    result["success"] = False
                    result["msg"] = "该文件已存在"
                    return JsonResponse(result)
                with open(f"{path}/{wl_file.name}", "wb+") as f:
                    for content in wl_file.chunks():
                        f.write(content)
            elif method == "add_dir":  # 新建文件夹
                if os.path.exists(path):
                    result["success"] = False
                    result["msg"] = "该文件夹已存在"
                else:
                    os.mkdir(path)
            elif method == "rename":
                new_name = request.POST.get("new_name")
                old_name = request.POST.get("old_name")
                if not old_name or not new_name:
                    result["msg"] = "文件或目录名不能为空"
                    result["success"] = False
                else:
                    os.rename(path + old_name, path + new_name)
            elif method == "get":
                file_info_list = []
                file_path = MEDIA_ROOT + request.POST.get("path", "")
                try:
                    file_name_list = os.listdir(file_path)
                except FileNotFoundError:
                    file_name_list = []
                    result["msg"] = "该文件不存在"
                for file_name in file_name_list:
                    is_dir = os.path.isdir(file_path + "/" + file_name)
                    file_info_list.append({
                        "file_name": file_name,
                        "is_dir": is_dir,
                        "file_size": "{}kb".format(os.path.getsize(file_path + "/" + file_name) // 1024) if not is_dir else "",
                        "create": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(f"{file_path}/{file_name}")))
                    })
                result["data"] = file_info_list
            return JsonResponse(result, safe=False)
    else:
        return HttpResponseRedirect("/admin")
