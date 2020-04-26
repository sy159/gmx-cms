from __future__ import absolute_import, unicode_literals

from mainsys.celery_run import celery_app

from celery import shared_task


'''
send_email.apply_async(args=[30,40], kwargs={'z':5})

# 其他参数
task_id:为任务分配唯一id，默认是uuid;
countdown : 设置该任务等待一段时间再执行，单位为s；
eta : 定义任务的开始时间；eta=time.time()+10;
expires : 设置任务时间，任务在过期时间后还没有执行则被丢弃；
retry : 如果任务失败后, 是否重试;使用true或false，默认为true
retry_policy : {},重试策略.如下：
    max_retries : 最大重试次数, 默认为 3 次.
    interval_start : 重试等待的时间间隔秒数, 默认为 0 , 表示直接重试不等待.
    interval_step : 每次重试让重试间隔增加的秒数, 可以是数字或浮点数, 默认为 0.2
    interval_max : 重试间隔最大的秒数, 即 通过 interval_step 增大到多少秒之后, 就不在增加了, 可以是数字或者浮点数, 默认为 0.2 .
# 如下
add.apply_async((2, 2), retry=True, retry_policy={
    'max_retries': 3,
    'interval_start': 0,
    'interval_step': 0.2,
    'interval_max': 0.2,
})

priority：任务队列的优先级，0到255之间，对于rabbitmq来说0是最高优先级；
headers：为任务添加额外的消息；
link：任务成功执行后的回调方法；是一个signature对象；可以用作关联任务；
link_error: 任务失败后的回调方法，是一个signature对象；
'''

@celery_app.task(name="send_email")
def send_email(x, y):
    import time
    time.sleep(10)
    return x**y


@shared_task()
def schedule_test():  # 定时任务
    import datetime
    now = str(datetime.datetime.now())
    with open("xx.txt", "w") as f:
        f.write(now)
    print(now)
    return now
