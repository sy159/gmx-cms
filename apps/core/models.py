from __future__ import unicode_literals

from django.db import models


# 系统配置
class WebSettings(models.Model):
    DEBUG = models.CharField('是否启用调试', null=True, max_length=5, default='True', choices=(('False', "否"), ('True', "是")))
    ALLOWED_HOSTS = models.CharField('授权的域名', max_length=200, null=True, default="*", help_text="多个用','分隔")
    SITE_HEADER = models.CharField('后台头部', max_length=200, null=True, default="后台管理系统")
    SECRET_KEY = models.CharField('系统SECRET_KEY', max_length=200, null=True, default="G5M2X0fas@#@ef^sc)r^(_g+Ag")
    # 如果开起UpdateCacheMiddleware，FetchFromCacheMiddleware作为全站缓存使用
    CACHE_MIDDLEWARE_SECONDS = models.IntegerField("缓存时间", default=900, null=True, help_text="全站缓存的默认时间(需要加入cache中间件)，单位：秒")
    CACHE_MIDDLEWARE_KEY_PREFIX = models.CharField("缓存前缀", max_length=20, null=True, default="gmx", help_text="缓存key前缀")
    SESSION_COOKIE_SECONDS = models.IntegerField("session过期时间", default=1800, null=True, help_text="全站session过期时间，单位：秒")
    SESSION_EXPIRE_AT_BROWSER_CLOSE = models.CharField('关闭浏览器session是否失效', max_length=5, null=True, default="True", choices=(("False", "否"), ("True", "是")))
    FILE_UPLOAD_MAX_MEMORY_SIZE = models.IntegerField('文件上传大小上限', default=8388608, null=True, help_text='设置最大允许上传的文件大小，单位：bit。8388608=8M')
    ACCESS_TOKEN_EXPIRE_SECONDS = models.IntegerField("访问token有效时间", default=60, null=True, help_text='oauth2访问token有效时间(秒),超时之后请求受保护的资源将失败')
    AUTHORIZATION_CODE_EXPIRE_SECONDS = models.IntegerField("授权码(grant code)有效时间", default=600, null=True, help_text='授权码有效时间(秒),在此持续时间之后请求访问令牌将失败')
    EMAIL_HOST = models.CharField('SMTP服务器', max_length=50, blank=True, null=True, default="smtp.163.com", help_text="邮件发送服务器地址，比如：smtp.ym.163.com")
    EMAIL_PORT = models.IntegerField('SMTP端口号', null=True, blank=True, default=25)
    EMAIL_SUBJECT_PREFIX = models.CharField('邮件标题的前缀', max_length=20, null=True, blank=True, default="")
    EMAIL_HOST_USER = models.CharField("发件邮箱", blank=True, null=True, max_length=50, default="")
    EMAIL_HOST_PASSWORD = models.CharField('发件邮箱密码', blank=True, null=True, max_length=20, default="", help_text="163邮箱使用授权码")
    EMAIL_USE_TLS = models.CharField('是否开启安全链接', max_length=5, null=True, default="True", choices=(("False", "否"), ("True", "是")))

    class Meta:
        verbose_name = '开发者选项'
        verbose_name_plural = verbose_name
        db_table = 'web_settings'

    def __str__(self):
        return '站点全局配置'

    def save(self, *args, **kwargs):
        if self.id:  # 添加新配置（更新没有self.id）,只留一个配置
            WebSettings.objects.exclude(id=self.id).delete()
        ALLOWED_HOSTS = ""
        for s in self.ALLOWED_HOSTS.split(","):
            ALLOWED_HOSTS += '"' + s.strip() + '", '
        config_text = '''# 本文件记录系统相关配置

# 重新分配
SECRET_KEY = "%s"

FILE_UPLOAD_PERMISSIONS = 0o644  # 文件上传权限
FILE_UPLOAD_MAX_MEMORY_SIZE = %s  # 最大文件上传size

# 开起全站缓存使用，不需要的需要使用never_cache
CACHE_MIDDLEWARE_SECONDS = %s  # 默认缓存过期时间
CACHE_MIDDLEWARE_KEY_PREFIX = "%s"  # 缓存前缀

DEBUG = %s

ALLOWED_HOSTS = [%s]

SITE_HEADER = '%s'

# session设置
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'  # session存储位置（默认是db）
SESSION_SAVE_EVERY_REQUEST = True  # SESSION_COOKIE_AGE 和 SESSION_EXPIRE_AT_BROWSER_CLOSE 这两个参数只有在 SESSION_SAVE_EVERY_REQUEST 为 True 时才有效
SESSION_COOKIE_AGE = %s  # session过期时间60分钟
SESSION_EXPIRE_AT_BROWSER_CLOSE = %s  # 是否在用户关闭浏览器时过期会话

# oauth2相关配置
OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
    },

    'CLIENT_ID_GENERATOR_CLASS': 'oauth2_provider.generators.ClientIdGenerator',
    'ACCESS_TOKEN_EXPIRE_SECONDS': %s, # 访问token有效时间
    'AUTHORIZATION_CODE_EXPIRE_SECONDS': %s, # 授权码(grant code)有效时间，在此持续时间之后请求访问令牌将失败
}

# Email设置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = '%s'  # QQ邮箱SMTP服务器(邮箱需要开通SMTP服务)
EMAIL_PORT = %s  # QQ邮箱SMTP服务端口
EMAIL_HOST_USER = '%s'  # 我的邮箱帐号
EMAIL_HOST_PASSWORD = '%s'  # 授权码
EMAIL_SUBJECT_PREFIX = '%s'  # 为邮件标题的前缀,默认是'[django]'
EMAIL_USE_TLS = %s  # 开启安全链接
DEFAULT_FROM_EMAIL = SERVER_EMAIL = EMAIL_HOST_USER  # 设置发件人
''' % (self.SECRET_KEY, str(self.FILE_UPLOAD_MAX_MEMORY_SIZE), str(self.CACHE_MIDDLEWARE_SECONDS), self.CACHE_MIDDLEWARE_KEY_PREFIX, self.DEBUG, ALLOWED_HOSTS, self.SITE_HEADER,
       str(self.SESSION_COOKIE_SECONDS), self.SESSION_EXPIRE_AT_BROWSER_CLOSE, str(self.ACCESS_TOKEN_EXPIRE_SECONDS), str(self.AUTHORIZATION_CODE_EXPIRE_SECONDS), self.EMAIL_HOST,
       str(self.EMAIL_PORT), self.EMAIL_HOST_USER, self.EMAIL_HOST_PASSWORD, self.EMAIL_SUBJECT_PREFIX, self.EMAIL_USE_TLS)
        with open("mainsys/config.py", "w", encoding="utf-8") as f:
            f.write(config_text)
        super().save(*args, **kwargs)
        # 重新加载代码(在uwsgi的ini文件中配置py-autoreload = 1  # 代码修改后自动重启)


# 站点配置
class SiteSetting(models.Model):
    theme = (("default", "默认"), ("blue", "蓝色"))
    SITE_HOST = models.CharField('站点域名', max_length=50, null=True, unique=True)
    SITE_NAME = models.CharField('系统名称', max_length=50, null=True, blank=True, default='如何好听')
    SYSTEM_THEME = models.CharField('系统主题', max_length=50, null=True, blank=True, choices=theme, default="default")
    HOME_URL = models.CharField('首页url', max_length=50, null=True, blank=True, default="", help_text="url不需要带域名，示例:'/index/about/'")
    COMPANY_NAME = models.CharField('公司名称', max_length=50, null=True, blank=True, default='如何好听')
    COMPANY_INFO = models.CharField('公司简介', max_length=50, null=True, blank=True, default='猪猪女孩')
    COMPANY_ADDRESS = models.CharField('公司地址', max_length=50, null=True, blank=True, default='重庆市')
    COMPANY_ICP = models.CharField('公司ipc备案号', max_length=50, null=True, blank=True)
    QQ = models.CharField('客服QQ', max_length=15, null=True, blank=True, default='1138559515')
    TEL = models.CharField('联系方式', max_length=15, null=True, blank=True, default='187****2553')

    class Meta:
        verbose_name = '多域名设置'
        verbose_name_plural = verbose_name
        db_table = 'site_settings'

    def __str__(self):
        return '%s-个性设置' % self.SITE_HOST

    @staticmethod
    def change_site_config():
        site_objs = SiteSetting.objects.all()
        site_dict = dict()
        for site_obj in site_objs:
            site_dict[site_obj.SITE_HOST] = {
                "site_name": site_obj.SITE_NAME or "如何好听",
                "system_theme": site_obj.SYSTEM_THEME or "default",
                "home_url": site_obj.HOME_URL or "",
                "company_name": site_obj.COMPANY_NAME or "如何好听",
                "company_info": site_obj.COMPANY_INFO or "gmx",
                "company_addr": site_obj.COMPANY_ADDRESS or "重庆",
                "company_icp": site_obj.COMPANY_ICP or "",
                "qq": site_obj.QQ or "1138559515",
                "tel": site_obj.TEL or "187****2553",
            }
        webconfig_str = f'# 本文件记录多域名配置\n\nsite_conf = {site_dict}\n'
        with open("mainsys/webconfig.py", "w", encoding="utf-8") as f:
            f.write(webconfig_str)

    def save(self, *args, **kwargs):
        SiteSetting.change_site_config()
        super().save()

    def delete(self, using=None, keep_parents=False):
        SiteSetting.change_site_config()
        super().delete()
