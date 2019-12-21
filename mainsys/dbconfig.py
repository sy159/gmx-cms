""""
本文件记录数据库相关配置
"""

# 重新分配
SECRET_KEY = "l*8!si1_0)23jy@+7o68t+&dnz^sc)r^tm0_efh=#=gh45&^ics3452345"

# elasticsearch连接配置
es_conf = {
    "host": "http://127.0.0.1:9200/",
    "user": "accounts",
    "password": "123456",
}
# mq连接配置
mq_conf = {
    "host": "http://127.0.0.1:15672/",
    "user": "accounts",
    "password": "123456",
}

# 缓存设置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://49.234.18.154:6380/0",  # redis地址
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},  # 连接池（最大连接数）
            "PASSWORD": ""
        }
    }
}

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'mainsys.db_pool.mysql',
        'NAME': "handilajidui",
        'USER': "root",
        'PASSWORD': "zx.123",
        'HOST': "192.168.4.201",
        'PORT': 3306,
        # 持久化(每个数据库连接的最大存活时间，以秒为单位。0表示在每个请求结束时关闭数据库连接，None表示无限的持久连接),小于数据库的maxWait
        'CONN_MAX_AGE': 20,
        # 数据库连接池大小，mysql 总连接数大小为：连接池大小 * 服务进程数，默认5个(db_pool中base设置)
        'DB_POOL_SIZE': 20,
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
    'db2': {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "test",
        "USER": "root",
        "PASSWORD": "zx.123",
        "HOST": "192.168.4.203",
        'PORT': 3306,
    }
}

# 多数据库联用配置
DATABASE_DICT = {
    'db2': 'db2',
}


# 配置多数据库路由规则，实现读写分离等操作
class DatabaseAppsRouter(object):
    def db_for_read(self, model, **hints):
        """"Point all read operations to the specific database."""
        if model._meta.app_label in DATABASE_DICT:
            return DATABASE_DICT[model._meta.app_label]
        return None

    def db_for_write(self, model, **hints):
        """Point all write operations to the specific database."""
        if model._meta.app_label in DATABASE_DICT:
            return DATABASE_DICT[model._meta.app_label]
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Allow any relation between apps that use the same database."""
        db_obj1 = DATABASE_DICT.get(obj1._meta.app_label)
        db_obj2 = DATABASE_DICT.get(obj2._meta.app_label)
        if db_obj1 and db_obj2:
            if db_obj1 == db_obj2:
                return True
            else:
                return False
        return None

    # for Django 1.4 - Django 1.6
    def allow_syncdb(self, db, model):
        """Make sure that apps only appear in the related database."""

        if db in DATABASE_DICT.values():
            return DATABASE_DICT.get(model._meta.app_label) == db
        elif model._meta.app_label in DATABASE_DICT:
            return False
        return None

    # Django 1.7 -
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db in DATABASE_DICT.values():
            return DATABASE_DICT.get(app_label) == db
        elif app_label in DATABASE_DICT:
            return False
        return None


# 如需启用配置的多数据库路由规则，则反注释掉下面语句
DATABASE_ROUTERS = ['mainsys.dbconfig.DatabaseAppsRouter']
