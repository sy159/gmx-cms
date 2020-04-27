from django.contrib import admin

from apps.core.models import *


@admin.register(WebSettings)
class WebSettingsAdmin(admin.ModelAdmin):
    fieldsets = (("基础设置", {"fields": ["DEBUG", "ALLOWED_HOSTS", "FILE_UPLOAD_MAX_MEMORY_SIZE", "SITE_HEADER"]}),
                 ("缓存及session设置", {"fields": ["CACHE_MIDDLEWARE_SECONDS", "CACHE_MIDDLEWARE_KEY_PREFIX", "SESSION_COOKIE_SECONDS", "SESSION_EXPIRE_AT_BROWSER_CLOSE"]}),
                 ("OAuth2设置", {"fields": ["ACCESS_TOKEN_EXPIRE_SECONDS", "AUTHORIZATION_CODE_EXPIRE_SECONDS"]}),
                 ("邮箱配置", {"fields": ["EMAIL_HOST", "EMAIL_PORT", "EMAIL_SUBJECT_PREFIX", "EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD", "EMAIL_USE_TLS"]}),
                 )
    radio_fields = {"DEBUG": admin.HORIZONTAL, "EMAIL_USE_TLS": admin.HORIZONTAL, "SESSION_EXPIRE_AT_BROWSER_CLOSE": admin.HORIZONTAL}

    # 是否有添加权限
    def has_add_permission(self, request):
        if request.user.username in ["root", ]:
            return True
        return False

    # 是否有删除权限
    def has_delete_permission(self, request, obj=None):
        return False

    # 是都有修改权限
    def has_change_permission(self, request, obj=None):
        if request.user.username in ["root", ]:
            return True
        return False


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    fieldsets = (("站点信息", {"fields": ["SITE_HOST", "SITE_NAME"]}),
                 ("公司信息", {"fields": ["COMPANY_NAME", "COMPANY_INFO", "COMPANY_ADDRESS", "COMPANY_ICP", "QQ", "TEL"]}),
                 )
    list_display = ['SITE_HOST', 'SITE_NAME', 'COMPANY_NAME']
    list_display_links = ['SITE_HOST']  # 可连接点进
    list_filter = ['SITE_HOST', "SITE_NAME"]

    def has_delete_permission(self, request, obj=None):
        if request.user.username in ["root", ]:
            return True
        return False

    # 只允许查看属于当前域名下的用户
    def get_queryset(self, request):
        qs = super(SiteSettingAdmin, self).get_queryset(request)
        if request.user.username in ["root", ]:
            return qs
        return qs.filter(SITE_HOST=request.get_host())
