from datetime import timedelta

from kombu import Exchange, Queue

from mainsys.dbconfig import mq_conf, redis_conf

# celery配置(http://docs.celeryproject.org/en/latest/userguide/configuration.html)
# mq为：amqp://username:passwd@host:port/虚拟主机名；redis：redis://username:passwd@host:port/db

broker_url = 'amqp://%s:%s@%s:%d/%s' % (mq_conf.get("user"), mq_conf.get("pwd"), mq_conf.get("host"), mq_conf.get("port"), mq_conf.get("vhost"))
result_backend = 'redis://%s:%d/%s' % (redis_conf.get("host"), redis_conf.get("port"), redis_conf.get("db"))  # 结果存储地址
task_serializer = 'json'  # 任务序列化方式
result_serializer = 'json'  # 任务执行结果序列化方式
accept_content = ["json"]  # 指定任务接受的内容类型
enable_utc = True  # 启动时区设置
timezone = 'Asia/Shanghai'
# task_acks_late = True  # 任务发送完成是否需要确认，这一项对性能有一点影响
C_FORCE_ROOT = True  # 允许在root下运行
result_compression = 'zlib'  # # 压缩方案选择，可以是zlib, bzip2，默认是发送没有压缩的数据
result_expires = 60 * 60 * 24  # 任务结果过期时间(结果最长保存时间),celery任务执行结果的超时时间
task_time_limit = 60 * 30  # 在30分钟内完成单个任务，否则执行该任务的worker将被杀死，任务移交给父进程
worker_max_tasks_per_child = 200  # 每个worker执行了多少任务就会死掉，默认是无限的(可防止内存泄露)
worker_prefetch_multiplier = 2  # celery worker 每次去rabbitmq预取任务的数量(默认值4)
# worker_concurrency = 4  # celery worker的并发数，默认是服务器的内核数目,也是命令行-c参数指定的数目

# 队列
task_queues = (
    # 队列名 exchange名 routing_key (delivery_mode=2消息持久化，durable=True队列持久化)
    Queue("celery_test", Exchange("celery", delivery_mode=2), routing_key="test", durable=True),
)
# 路由
task_routes = {
    'send_email': {"queue": "celery_test", "routing_key": "test"},
}

# 这里是定时任务的配置
CELERY_BEAT_SCHEDULE = {
    'task_method': {  # 随便起的名字
        'task': 'schedule_test',  # 需要执行定时任务的函数名
        'schedule': timedelta(seconds=15),  # 名字为task_method的定时任务, 每10秒执行一次
        # "args": (4,9), # 参数
        'options': {
            'queue': 'beat_queue',  # 指定要使用的队列
        }
    },
}
