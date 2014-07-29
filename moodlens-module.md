# Moodlens-module 配置
##1.功能说明
###moodlens即系统中情感分析的部分，分为两部分：case/moodlens/，case/cron/moodlens/
前者处理的是前段页面与mysql数据库之间的调用，后者是利用xapian索引生成数据存入mysql中的database
run.py作为测试入口，在浏览器上通过/moodlens/weibo查看该部分的功能
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
