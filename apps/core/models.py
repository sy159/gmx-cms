from django.db import models,transaction

class WebSettings(models.Model):
    DEBUG = models.CharField('是否启用调试', null=True, max_length=5, default='True', choices=(('False', "否"), ('True', "是")))
    ALLOWED_HOSTS = models.CharField('授权的域名', max_length=200, null=True, default="*", help_text="多个用','分隔")
    # 如果开起UpdateCacheMiddleware，FetchFromCacheMiddleware作为全站缓存使用
    CACHE_MIDDLEWARE_SECONDS = models.IntegerField("缓存时间", default=900, null=True, help_text="全站缓存的默认时间(需要加入cache中间件)，单位：秒")
    CACHE_MIDDLEWARE_KEY_PREFIX = models.CharField("缓存前缀", max_length=20, null=True, default="gmx", help_text="缓存key前缀")
    SESSION_COOKIE_SECONDS = models.IntegerField("session过期时间", default=1800, null=True, help_text="全站session过期时间，单位：秒")
    SESSION_EXPIRE_AT_BROWSER_CLOSE = models.BooleanField('关闭浏览器session是否失效', null=True, default=True, choices=((False, "否"), (True, "是")))
    FILE_UPLOAD_MAX_MEMORY_SIZE = models.IntegerField('文件上传大小上限', default=8388608, null=True, help_text='设置最大允许上传的文件大小，单位：bit。8388608=8M')
    EMAIL_HOST = models.CharField('SMTP服务器', max_length=50, blank=True, null=True, default="smtp.163.com", help_text="邮件发送服务器地址，比如：smtp.ym.163.com")
    EMAIL_PORT = models.IntegerField('SMTP端口号', null=True, blank=True, default="25")
    EMAIL_SUBJECT_PREFIX = models.CharField('邮件标题的前缀', max_length=20, null=True, blank=True, default="")
    EMAIL_HOST_USER = models.CharField("发件邮箱", blank=True, null=True, max_length=50, default="")
    EMAIL_HOST_PASSWORD = models.CharField('发件邮箱密码', blank=True, null=True, max_length=20, default="", help_text="163邮箱使用授权码")
    EMAIL_USE_TLS = models.BooleanField('是否开启安全链接', blank=True, null=True, default=True, choices=((False, "否"), (True, "是")))

    class Meta:
        verbose_name = '开发者选项'
        verbose_name_plural = verbose_name
        db_table = 'web_settings'

    def __str__(self):
        return '开发者选项'

    def save(self, *args, **kwargs):
        if self.id:  # 添加新配置（更新没有self.id）,只留一个配置
            WebSettings.objects.exclude(id=self.id).delete()
        ALLOWED_HOSTS = ""
        for s in self.ALLOWED_HOSTS.split(","):
            ALLOWED_HOSTS += '"' + s.strip() + '", '
        config_text = '''# 本文件记录系统相关配置

FILE_UPLOAD_PERMISSIONS = 0o644  # 文件上传权限
FILE_UPLOAD_MAX_MEMORY_SIZE = 8388608  # 最大文件上传size

# 开起全站缓存使用，不需要的需要使用never_cache
CACHE_MIDDLEWARE_SECONDS = 3600  # 默认缓存过期时间
CACHE_MIDDLEWARE_KEY_PREFIX = "gmx"  # 缓存前缀

DEBUG = True

ALLOWED_HOSTS = ["*", ]

# session设置
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'  # session存储位置（默认是db）
SESSION_SAVE_EVERY_REQUEST = True  # SESSION_COOKIE_AGE 和 SESSION_EXPIRE_AT_BROWSER_CLOSE 这两个参数只有在 SESSION_SAVE_EVERY_REQUEST 为 True 时才有效
SESSION_COOKIE_AGE = 60 * 60  # session过期时间60分钟
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # 是否在用户关闭浏览器时过期会话

# Email设置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'  # QQ邮箱SMTP服务器(邮箱需要开通SMTP服务)
EMAIL_PORT = 25  # QQ邮箱SMTP服务端口
EMAIL_HOST_USER = 'xxxx@163.com'  # 我的邮箱帐号
EMAIL_HOST_PASSWORD = '163sqm'  # 授权码
EMAIL_SUBJECT_PREFIX = 'gmx'  # 为邮件标题的前缀,默认是'[django]'
EMAIL_USE_TLS = True  # 开启安全链接
DEFAULT_FROM_EMAIL = SERVER_EMAIL = EMAIL_HOST_USER  # 设置发件人
'''
        super(WebSettings, self).save(*args, **kwargs)


class SiteSetting(models.Model):
    SITE_HOST = models.CharField('站点域名', max_length=50, null=True)
    SITE_NAME = models.CharField('系统名称', max_length=50, null=True, default='如何好听')
    COMPANY_NAME = models.CharField('公司名称', max_length=50, null=True, default='如何好听')
    COMPANY_INFO = models.CharField('公司简介', max_length=50, null=True, default='猪猪女孩')
    COMPANY_ADDRESS = models.CharField('公司地址', max_length=50, null=True, default='重庆市')
    COMPANY_ICP = models.CharField('公司ipc备案号', max_length=50, null=True)
    QQ = models.CharField('客服QQ', max_length=15, null=True, default='1138559515')
    TEL = models.CharField('联系方式', max_length=15, null=True, default='187****2553')
