# 同步models
python3 manage.py makemigrations --empty appname
python3 manage.py makemigrations
python3 manage.py migrate
# 收集静态文件
python3 manage.py collectstatic
