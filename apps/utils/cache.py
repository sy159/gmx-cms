import logging
import os
import shutil
from hashlib import md5

from django.core.cache import cache

from mainsys.settings import CACHE_MIDDLEWARE_SECONDS, CACHE_MIDDLEWARE_KEY_PREFIX

add_log = logging.getLogger('my_logger')


def _hashed_key(key: str) -> str:
    prefix = CACHE_MIDDLEWARE_KEY_PREFIX if CACHE_MIDDLEWARE_KEY_PREFIX else "gmx"
    key = "%s-%s" % (prefix, key)
    return md5(key.encode("utf-8")).hexdigest()


def cache_set(key: str, value, timeout=-1):
    if timeout == -1:  # 默认采用系统设置缓存时间
        timeout = CACHE_MIDDLEWARE_SECONDS if CACHE_MIDDLEWARE_SECONDS else 1800
    return cache.set(_hashed_key(key), value, timeout)


def cache_get(key: str):
    return cache.get(_hashed_key(key))


def cache_del(key: str):
    return cache.delete(_hashed_key(key))


def cache_flushdb():
    try:
        from mainsys.settings import CACHES
        if CACHES["default"]["BACKEND"].split(".")[-1] == "FileBasedCache":  # 文件缓存
            from mainsys.settings import CACHE_ROOT
            filelist = os.listdir(CACHE_ROOT)
            for f in filelist:
                filepath = os.path.join(CACHE_ROOT, f)
                if os.path.isfile(filepath):
                    os.remove(filepath)
                elif os.path.isdir(filepath):
                    shutil.rmtree(filepath, True)
        elif CACHES["default"]["BACKEND"].split(".")[-1] == "RedisCache":  # redis缓存
            from django_redis import get_redis_connection
            get_redis_connection("default").flushdb()
    except Exception as e:
        add_log.error("全站缓存清楚请求异常：" + str(e))
        return False
    return True
