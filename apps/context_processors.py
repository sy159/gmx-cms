from __future__ import unicode_literals
from apps.core.utils import sys_information


def site_settings(request=None):
    from apps.core.models import SiteSetting
    site_obj = SiteSetting.objects.filter(SITE_HOST=request.get_host()).first()
    if site_obj:
        setting = {
            "site_host": site_obj.SITE_HOST or "",
            "site_name": site_obj.SITE_NAME or "",  # 系统名称
            "company_name": site_obj.COMPANY_NAME or "",  # 公司名称
            "company_info": site_obj.COMPANY_INFO or "",  # 公司简介
            "company_address": site_obj.COMPANY_ADDRESS or "",  # 公司地址
            "company_icp": site_obj.COMPANY_ICP or "",  # 公司ipc备案号
            "QQ": site_obj.QQ or "",
            "TEL": site_obj.TEL or "",
        }
    else:
        setting = {
            "site_host": request.get_host(),
            "site_name": "gmx",  # 系统名称
            "company_name": "gmx",  # 公司名称
            "company_info": "gmx ",  # 公司简介
            "company_address": "gmx",  # 公司地址
            "company_icp": "icp",  # 公司ipc备案号
            "QQ": "159****116",
            "TEL": "187****2553",
        }
    # 前端模板获取{{ settings.QQ }}
    return {"settings": setting}


# 服务器信息
def sys_info(request=None):
    return sys_information()
