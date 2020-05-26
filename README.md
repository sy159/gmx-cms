# 实现简单快速开发cms系统框架
## 功能简介
- 集成oauth2管理、系统日志、媒体库、多域名设置，开发者选项等基础功能，基于django admin与simpleui实现页面定制化以及后台管理功能快速开发

------------
## 环境安装
- #### Python3.6+
- #### 安装django2.2+
- #### 安装mysql5.7(utf-8)
- #### redis、rabbitmq（根据需求安装）
------------
## 项目配置
- #### 克隆源码
git clone https://github.com/sy159/gmx
- #### 安装依赖
python3 -m pip install -r requirements.txt
根据需求安装（oauth跟celery相关库不使用可不安装）
- #### 修改dbconfig配置
根据实际情况配置数据库地址及用户名密码等，如果不需要redis作为缓存就注释掉redis配置，使用默认的文件缓存
- #### settings配置
根据需求配置settings.py文件，如果不需要oauth在settings跟url下注释掉oauth相关配置即可


------------
## 命令启动
#### 命令参考mainsys/run.sh文件
- #### 创建数据库
python3 manage.py makemigrations
python3 manage.py migrate
如果某个app下的model没有生成，就是用**python3 manage.py makemigrations  appname**
如果需要oauth的话就执行，python3 manage.py migrate oauth2_provider
- #### 创建后台登录的超级用户
python3 manage.py createsuperuser
- #### 项目启动
python3 manage.py runserver 0.0.0.0:8000
------------
## 界面展示
- 首页

- 系统日志

- 媒体库

- 开发者选项
