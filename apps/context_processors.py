from __future__ import unicode_literals
from apps.core.utils import sys_information


def site_settings(request=None):
    from mainsys.webconfig import site_conf
    setting = site_conf.get(request.get_host())
    # 前端模板获取{{ settings.qq }}
    return {"settings": setting}


# 服务器信息
def sys_info(request=None):
    return sys_information()
