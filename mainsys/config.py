# 本文件记录系统相关配置

FILE_UPLOAD_PERMISSIONS = 0o644  # 文件上传权限
FILE_UPLOAD_MAX_MEMORY_SIZE = 8388608  # 最大文件上传size

# 开起全站缓存使用，不需要的需要使用never_cache
CACHE_MIDDLEWARE_SECONDS = 900  # 默认缓存过期时间
CACHE_MIDDLEWARE_KEY_PREFIX = "gmx"  # 缓存前缀

DEBUG = True

ALLOWED_HOSTS = ["*", ]

SITE_HEADER = '后台管理系统'

# session设置
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'  # session存储位置（默认是db）
SESSION_SAVE_EVERY_REQUEST = True  # SESSION_COOKIE_AGE 和 SESSION_EXPIRE_AT_BROWSER_CLOSE 这两个参数只有在 SESSION_SAVE_EVERY_REQUEST 为 True 时才有效
SESSION_COOKIE_AGE = 1800  # session过期时间60分钟
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # 是否在用户关闭浏览器时过期会话

# oauth2相关配置
OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
    },

    'CLIENT_ID_GENERATOR_CLASS': 'oauth2_provider.generators.ClientIdGenerator',
    'ACCESS_TOKEN_EXPIRE_SECONDS': 300, # 访问token有效时间
    'AUTHORIZATION_CODE_EXPIRE_SECONDS': 600, # 授权码(grant code)有效时间，在此持续时间之后请求访问令牌将失败
}

# Email设置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'  # QQ邮箱SMTP服务器(邮箱需要开通SMTP服务)
EMAIL_PORT = 25  # QQ邮箱SMTP服务端口
EMAIL_HOST_USER = '123@qq.com'  # 我的邮箱帐号
EMAIL_HOST_PASSWORD = '163sqm'  # 授权码
EMAIL_SUBJECT_PREFIX = 'gmx'  # 为邮件标题的前缀,默认是'[django]'
EMAIL_USE_TLS = True  # 开启安全链接
DEFAULT_FROM_EMAIL = SERVER_EMAIL = EMAIL_HOST_USER  # 设置发件人
