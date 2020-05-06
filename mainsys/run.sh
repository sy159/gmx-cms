# 同步models
python3 manage.py makemigrations --empty appname
python3 manage.py makemigrations
python3 manage.py migrate
# 收集静态文件
python3 manage.py collectstatic
# celery
celery -A mainsys.celery_run worker -l info
# oauth2
python3 manage.py migrate oauth2_provider
python3 manage.py cleartokens  # 清理过期的token