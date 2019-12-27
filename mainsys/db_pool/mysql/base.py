from __future__ import unicode_literals

import random

from django.core.exceptions import ImproperlyConfigured
from django.db.backends.mysql.base import DatabaseWrapper as _DatabaseWrapper

try:
    import MySQLdb as Database
    # import pymysql as Database
    # Database.install_as_MySQLdb()
except ImportError as err:
    raise ImproperlyConfigured(
        'Error loading MySQLdb module.\n'
        'Did you install mysqlclient?'
    ) from err

DEFAULT_DB_POOL_SIZE = 5


class DatabaseWrapper(_DatabaseWrapper):
    def get_new_connection(self, conn_params):
        # 获取 DATABASES 配置字典中的 DB_POOL_SIZE 参数
        pool_size = self.settings_dict.get('DB_POOL_SIZE') or DEFAULT_DB_POOL_SIZE
        return ConnectPool.instance(conn_params, pool_size).get_connection()

    def _close(self):
        return None  # 覆盖掉原来的 close 方法，查询结束后连接不会自动关闭


class ConnectPool(object):
    def __init__(self, conn_params, pool_size):
        self.conn_params = conn_params
        self.pool_size = pool_size
        self.connects = []

    # 实现连接池的单例
    @staticmethod
    def instance(conn_params, pool_size):
        if not hasattr(ConnectPool, '_instance'):
            ConnectPool._instance = ConnectPool(conn_params, pool_size)
        return ConnectPool._instance

    def get_connection(self):
        if len(self.connects) < self.pool_size:
            new_connect = Database.connect(**self.conn_params)
            self.connects.append(new_connect)
            return new_connect
        index = random.randint(0, self.pool_size - 1)  # 随机返回连接池中的连接
        try:
            # 检测连接是否有效，去掉性能更好，但建议保留
            self.connects[index].ping()
        except Exception:
            self.connects[index] = Database.connect(**self.conn_params)
        return self.connects[index]
