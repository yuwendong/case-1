# Moodlens-module 配置

##1.功能说明

moodlens即系统中情感分析模块，分为两部分：case/moodlens/，case/cron/moodlens/
前者处理的是前端页面与mysql数据库之间的调用，后者是利用xapian索引生成数据存入mysql中的database。
run.py作为测试入口，在浏览器上通过219.224.135.47:9005/moodlens/weibo查看该部分的功能


##2.配置内容

2.1 case/global_config.py

```
    MYSQL_HOST = '219.224.135.46'
    MYSQL_USER = 'root'
    MYSQL_DB = 'weibocase'
    XAPIAN_USER_DATA_PATH = '/home/ubuntu3/huxiaoqian/case_test/data/user-datapath/'
```


2.2 case/cron/config.py

```
    XAPIAN_WEIBO_DATA_PATH = '/home/ubuntu3/huxiaoqian/case/20140724/20140724/'
    XAPIAN_USER_DATA_PATH = '/home/ubuntu3/huxiaoqian/case_test/data/user-datapath/'
    LEVELDBPATH = '/home/ubuntu3/huxiaoqian/case_test/data/leveldbpath/'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:@219.224.135.46/weibocase?charset=utf8'
    DYNAMIC_XAPIAN_WEIBO_STUB_PATH = '/home/ubuntu3/huxiaoqian/case_test/data/stubpath/master_timeline_weibo_'
```


##3.相关安装

3.1 flask安装

```
    sudo pip install flask
```
完成flask安装后，将case/package_install/目录下的安装包复制到服务器/usr/local/lib/python2.7/dist-package/目录下。
在运行run.py过程中可能会出现'no module named ***'，则需要再使用easy_install对其进行安装。


3.2 Mysql安装

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
