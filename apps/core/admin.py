from django.contrib import admin
from django.http import HttpResponseRedirect

from apps.core.models import *
from apps.core.utils import admin_url


@admin.register(WebSettings)
class WebSettingsAdmin(admin.ModelAdmin):
    fieldsets = (("基础设置", {"fields": ["DEBUG", "ALLOWED_HOSTS", "FILE_UPLOAD_MAX_MEMORY_SIZE", "SITE_HEADER"]}),
                 ("缓存及session设置", {"fields": ["CACHE_MIDDLEWARE_SECONDS", "CACHE_MIDDLEWARE_KEY_PREFIX", "SESSION_COOKIE_SECONDS", "SESSION_EXPIRE_AT_BROWSER_CLOSE"]}),
                 ("OAuth2设置", {"fields": ["ACCESS_TOKEN_EXPIRE_SECONDS", "AUTHORIZATION_CODE_EXPIRE_SECONDS"]}),
                 ("邮箱配置", {"fields": ["EMAIL_HOST", "EMAIL_PORT", "EMAIL_SUBJECT_PREFIX", "EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD", "EMAIL_USE_TLS"]}),
                 )
    radio_fields = {"DEBUG": admin.HORIZONTAL, "EMAIL_USE_TLS": admin.HORIZONTAL, "SESSION_EXPIRE_AT_BROWSER_CLOSE": admin.HORIZONTAL}
    readonly_fields = ["SECRET_KEY",]
    only_special_user_fields = [("高级设置", {"fields": ["SECRET_KEY"]})]  # 只有特殊用户能看字段，配合get_fieldsets使用

    # 部分参数设置只读功能
    def get_readonly_fields(self, request, obj=None):
        if request.user.username in ["root"]:
            self.readonly_fields = []
        return self.readonly_fields

    # 是否有添加权限
    def has_add_permission(self, request):
        if request.user.username in ["root", ]:
            return True
        return False

    # 是否有删除权限
    def has_delete_permission(self, request, obj=None):
        return False

    # 是都有修改权限
    # def has_change_permission(self, request, obj=None):
    #     if request.user.username in ["root", ]:
    #         return True
    #     return False

    # 视图列表（网站全局配置就一个，直接跳转到change页面）
    def changelist_view(self, request, *args, **kwargs):
        all_obj = WebSettings.objects.all()
        if len(all_obj):
            obj = all_obj[0]
        else:
            obj = WebSettings()
            obj.save()
        return HttpResponseRedirect(admin_url(WebSettings, "change", object_id=obj.id))

    def get_fieldsets(self, request, obj=None):
        """
        Hook for specifying fieldsets.
        """
        if self.fieldsets:
            if request.user.username in ["root"]:
                return  tuple(list(self.fieldsets) + self.only_special_user_fields)
            return self.fieldsets
        return [(None, {'fields': self.get_fields(request, obj)})]


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
