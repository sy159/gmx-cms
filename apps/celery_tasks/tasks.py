from __future__ import absolute_import, unicode_literals

from celery import shared_task


@shared_task
def schedule_test():  # 定时任务
    import datetime
    now = str(datetime.datetime.now())
    print(now)
    return now
