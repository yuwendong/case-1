# Moodlens-module 配置

##1.功能说明

moodlens即系统中情感分析模块，分为两部分：case/moodlens/，case/cron/moodlens/
前者处理的是前端页面与mysql数据库之间的调用，后者是利用xapian索引生成数据存入mysql中的database。
run.py作为测试入口，在浏览器上通过219.224.135.47:9005/moodlens/weibo查看该部分的功能


##2.配置内容

2.1 case/global_config.py

```
    MYSQL_HOST = '219.224.135.47'
    MYSQL_USER = 'root'
    MYSQL_DB = 'weibocase'
    XAPIAN_USER_DATA_PATH = '/home/ubuntu3/huxiaoqian/case_test/data/user-datapath/'
```


2.2 case/cron/config.py

```
    XAPIAN_WEIBO_DATA_PATH = '/home/ubuntu3/huxiaoqian/case/20140724/20140724/'
    XAPIAN_USER_DATA_PATH = '/home/ubuntu3/huxiaoqian/case_test/data/user-datapath/'
    LEVELDBPATH = '/home/ubuntu3/huxiaoqian/case_test/data/leveldbpath/'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:@219.224.135.47/weibocase?charset=utf8'
    DYNAMIC_XAPIAN_WEIBO_STUB_PATH = '/home/ubuntu3/huxiaoqian/case_test/data/stubpath/master_timeline_weibo_'
```


##3.相关安装
预先安装
```
apt-get install python-dev
```
3.1 easy_install配置
```
wget https://bootstrap.pypa.io/ez_setup.py
python ez_setup.py
```

3.2 pip install安装
```
easy_install pip
```

3.3 flask安装

```
    sudo pip install flask
```
完成flask安装后，将case/package_install/目录下的压缩文件package_install.zip解压缩后，将以下文件复制到服务器/usr/local/lib/python2.7/dist-packages/目录下。
```
    Flask_Admin-1.0.4-py2.7.egg
    Flask_DebugToolbar-0.8.0-py2.7.egg
    Flask_Login-0.1.3-py2.7.egg
    Flask_PyMongo-0.1.2-py2.7.egg
    Flask_PyMongo-0.2.1-py2.7.egg
    Flask_SQLAlchemy-0.16-py2.7.egg
    Flask_WTF-0.8.2-py2.7.egg
    Flask-0.9-py2.7.egg
    Flask-0.10.1-py2.7.egg-info
    sqlalchemy
    SQLAlchemy-0.8.0-py2.7-linux-x86_64.egg
```
在运行run.py过程中可能会出现'no module named ***'，则需要再使用easy_install对其进行安装。
如
```
easy_install flask_debugtoolbar
easy_install flask_admin
easy_install flask_login
easy_install flask_wtf
```


3.4 Mysql安装

```
   sudo apt-get install mysql-server
   sudo easy-install mysql-python
```
在mysql的安装中要求输入密码时，不要设置密码。
如果在安装时没有设置密码，而在运行过程中仍被要求密码，则说明曾经安装过mysql并且其相关注册信息残留。这时按照如下操作跳过权限认证，并以root身份登录：
```
    # /usr/bin/mysqld_safe --skip-grant-tables
    # mysql -u root
```
