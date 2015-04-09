# Docker封装具体实施步骤

## 1 使用docker在91、92、93上部署scrapy_guba_redis 

### 1.1 安装ubuntu操作系统基础镜像ubuntu:base

参考http://www.it165.net/os/html/201408/9126.html

(1)从openvz下载一个ubuntu14.04的模板
```
wget http://download.openvz.org/template/precreated/ubuntu-14.04-x86_64.tar.gz
```

(2)创建ubuntu:base基础镜像
```
cat ubuntu-14.04-x86_64.tar.gz |docker import - ubuntu:base
```

### 1.2 创建ubuntu操作系统latest镜像ubuntu:latest

(1)docker run -t -i ubuntu:base /bin/bash 进入虚拟机 编辑apt软件源vim /etc/apt/sources.list，删除里面的内容，粘帖上xubuntu 14.04.1 LTS的源
```
# deb cdrom:[Xubuntu 14.04.1 LTS _Trusty Tahr_ - Release amd64 (20140723)]/ trusty main multiverse restricted universe

# See http://help.ubuntu.com/community/UpgradeNotes for how to upgrade to
# newer versions of the distribution.
deb http://cn.archive.ubuntu.com/ubuntu/ trusty main restricted
deb-src http://cn.archive.ubuntu.com/ubuntu/ trusty main restricted

## Major bug fix updates produced after the final release of the
## distribution.
deb http://cn.archive.ubuntu.com/ubuntu/ trusty-updates main restricted
deb-src http://cn.archive.ubuntu.com/ubuntu/ trusty-updates main restricted

## N.B. software from this repository is ENTIRELY UNSUPPORTED by the Ubuntu
## team. Also, please note that software in universe WILL NOT receive any
## review or updates from the Ubuntu security team.
deb http://cn.archive.ubuntu.com/ubuntu/ trusty universe
deb-src http://cn.archive.ubuntu.com/ubuntu/ trusty universe
deb http://cn.archive.ubuntu.com/ubuntu/ trusty-updates universe
deb-src http://cn.archive.ubuntu.com/ubuntu/ trusty-updates universe

## N.B. software from this repository is ENTIRELY UNSUPPORTED by the Ubuntu 
## team, and may not be under a free licence. Please satisfy yourself as to 
## your rights to use the software. Also, please note that software in 
## multiverse WILL NOT receive any review or updates from the Ubuntu
## security team.
deb http://cn.archive.ubuntu.com/ubuntu/ trusty multiverse
deb-src http://cn.archive.ubuntu.com/ubuntu/ trusty multiverse
deb http://cn.archive.ubuntu.com/ubuntu/ trusty-updates multiverse
deb-src http://cn.archive.ubuntu.com/ubuntu/ trusty-updates multiverse

## N.B. software from this repository may not have been tested as
## extensively as that contained in the main release, although it includes
## newer versions of some applications which may provide useful features.
## Also, please note that software in backports WILL NOT receive any review
## or updates from the Ubuntu security team.
deb http://cn.archive.ubuntu.com/ubuntu/ trusty-backports main restricted universe multiverse
deb-src http://cn.archive.ubuntu.com/ubuntu/ trusty-backports main restricted universe multiverse

deb http://security.ubuntu.com/ubuntu trusty-security main restricted
deb-src http://security.ubuntu.com/ubuntu trusty-security main restricted
deb http://security.ubuntu.com/ubuntu trusty-security universe
deb-src http://security.ubuntu.com/ubuntu trusty-security universe
deb http://security.ubuntu.com/ubuntu trusty-security multiverse
deb-src http://security.ubuntu.com/ubuntu trusty-security multiverse

## Uncomment the following two lines to add software from Canonical's
## 'partner' repository.
## This software is not part of Ubuntu, but is offered by Canonical and the
## respective vendors as a service to Ubuntu users.
# deb http://archive.canonical.com/ubuntu trusty partner
# deb-src http://archive.canonical.com/ubuntu trusty partner

## This software is not part of Ubuntu, but is offered by third-party
## developers who want to ship their latest software.
deb http://extras.ubuntu.com/ubuntu trusty main
deb-src http://extras.ubuntu.com/ubuntu trusty main
deb http://packages.elasticsearch.org/elasticsearch/1.4/debian stable main
# deb-src http://packages.elasticsearch.org/elasticsearch/1.4/debian stable main
# deb-src http://packages.elasticsearch.org/elasticsearch/1.4/debian stable main
```

(2)apt-get update更新, exit虚拟机, docker ps -a, docker commit containerid ubuntu, 从而创建ubuntu:latest镜像

### 1.3 从ubuntu:latest创建面向scrapy任务的scrapy_guba_redis:0.1.0镜像

(1)clone 代码库
```
mkdir docker_scrapy_guba_redis
cd docker_scrapy_guba_redis
git clone https://github.com/linhaobuaa/scrapy_guba_redis.git 
```

(2)vim Dockerfile
```
FROM ubuntu:latest

MAINTAINER HuangXiaojun

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y gcc make python-dev python-setuptools git

RUN apt-get install libxml2 libxml2-dev libxslt-dev libxslt1-dev
ADD scrapy_guba_redis /
RUN easy_install pip
RUN apt-get install python-lxml openssl
RUN apt-get install libffi-dev
RUN apt-get install -y libssl-dev
RUN easy_install pyOpenSSL
RUN pip install scrapy
RUN pip install beautifulsoup
RUN pip install redis
RUN pip install pymongo
```

(3) docker build -t scrapy_guba_redis:0.1.0 .

(4) 运行list爬虫
```
docker run scrapy_guba_redis:0.1.0 scrapy crawl guba_stock_list_realtime_redis_spider --loglevel=INFO
```

(5) 运行detail爬虫
```
docker run scrapy_guba_redis:0.1.0 scrapy crawl guba_stock_detail_realtime_redis_spider --loglevel=INFO
```

### 1.4 将scrapy_guba_redis:0.1.0 push 到 dockerhub上
```
docker commit containerid rcsc/scrapy_guba_redis
docker push rscs/scrapy_guba_redis
```

### 1.5 提交任务到marathon
(1) 编辑Docker_list.json如下
```
{
  "container": {
    "type": "DOCKER",
    "docker": {
      "image": "scrapy_guba_redis:0.1.0"
    }
  },
  "id": "scrapygubaredislist",
  "instances": 1,
  "cpus": 1,
  "mem": 512,
  "uris": [],
  "cmd": "scrapy crawl guba_stock_list_realtime_redis_spider --loglevel=INFO --logfile=list.log"
}
```

(2) 提交任务到marathon master
```
curl -X POST -H "Content-Type: application/json" 219.224.135.91:8080/v2/apps -d@Docker_list.json
```

(3) marathon管理页面http://219.224.135.91:8080

### 1.6 使用docker部署elasticsearch+logstash+kibana+logstash_forwarder收集scrapy docker产生的日志

说明：在219.224.135.91上使用docker部署elasticsearch+logstash+kibana，在91、92、93上使用docker分别部署scrapy+logstash_forwarder

(1) setup elasticsearch  
```
docker pull denibertovic/elasticsearch
git clone https://github.com/denibertovic/elasticsearch-dockerfile.git
cd elasticsearch-dockerfile
docker run --name elasticsearch -v `pwd`/config-example:/opt/elasticsearch/config -p 9200:9200 -p 9300:9300 -d -t denibertovic/elasticsearch
```

(2) setup kibana  http://219.224.135.91:5601
```
docker pull denibertovic/kibana
git clone https://github.com/denibertovic/kibana-dockerfile.git
cd kibana-dockerfile
docker run --name kibana -d -p 5601:5601 -v /tmp/logs:/logs -v `pwd`/config-example:/kibana/config -t denibertovic/kibana
```

(3) setup logstash
注意把产生的certs传给logstash-forwarder
```
git clone https://github.com/denibertovic/logstash-dockerfile.git
cd logstash-dockerfile
mkdir -p certs && cd certs
openssl req -subj '/CN=localhost/' -x509 -batch -nodes -newkey rsa:2048 -keyout logstash-forwarder.key -out logstash-forwarder.crt
docker pull denibertovic/logstash
docker run --name logstash -p 5043:5043 -p 514:514 -v `pwd`/certs:/opt/certs -v `pwd`/conf-example:/opt/conf --link elasticsearch:elasticsearch -d -t denibertovic/logstash
```

(4) 每台机上部署一个 logstash-forwarder 参考https://github.com/linhaobuaa/logstash-forwarder-dockerfile
```
git clone https://github.com/linhaobuaa/logstash-forwarder-dockerfile
cd logstash-forwarder-dockerfile
docker build -t logstash-forwarder .
docker run --name forwarder -v /tmp/test:/tmp/test -v `pwd`/conf-example:/opt/conf -v `pwd`/certs:/opt/certs -v /tmp/feeds -d -t logstash-forwarder
```

(5) 每台机器上部署一个scrapy



## 2 其他说明

(1)利用docker容器技术对本项目进行封装，首先考虑该项目所依赖的运行环境编写Do    ckerfile文件；然后利用该文件构建相应的docker镜像；最后将本项目存储于mongodb>    上的数据转入到docker本地的mongodb中。具体步骤如下：

(2)根据项目所依赖的运行环境编写Dockerfile文件。

(3)Dockerfile是一个镜像的表示，可以通过Dockerfile来描述构建镜像的步骤，可以

(4)利用它构建一个容器。本项目所依赖的环境如下：

(5)python 的基本工具，如python-pip、python-dev、python-setuptools等

(6)安装运行所需库时所用到的下载、解压缩、编译工具，如git、wget、bzip2、make    等工具

(7)scwc中文分词工具

(8)所需python库包括：scipy、numpy、pyscws、xapian_case、FileLock、python-Le    venshtein、pymongo、gensim、Flask等

(9)MongoDB

(10)利用编写好的Dockerfile文件和该项目源文件构建docker镜像。

(11)利用mongodump和mongorestore工具将所需数据从外部数据库导入到docker容器内部的数据库。

#常用的Docker命令

	构建自己的docker镜像(重要)
docker build -t 镜像名Dockerfile路径
示例： docker build -t kmeans:1.0 . 
	列出镜像列表
docker images
	退出docker
exit 
	启动容器
# 交互式进入容器(重要)
docker run -i -t 镜像名 /bin/bash  
#执行普通命令
docker run 镜像名 执行的命令
示例：docker run kmeans:1.0 python app.py
          docker run kmeans:1.0 echo “hello world”  
#-p参数将container的端口映射到宿主机的端口(重要)
docker run -i -t -p host_port:contain_port
示例：docker run -i -t -p 8080:8080 python app.py
	查看容器
# 列出当前所有正在运行的container
docker ps
# 列出所有的container
docker ps -a
# 列出最近一次启动的container
docker ps -l
	保存对容器的修改(重要)
docker commit ID 新的镜像名
示例：


其它命令详见：
http://www.tuicool.com/articles/7V7vYn

http://blog.tankywoo.com/docker/2014/05/08/docker-4-summary.html

如何利用Dockerfile构建docker镜像:
http://blog.csdn.net/we_shell/article/details/38445979


opinion_news服务相关注意事项

	Dockerfile以及服务代码目录保存路径：
服务器：219.224.135.93
路径：/root/Documents，包括Dockerfile和OpinionNews两项
	在docker中运行mongo 会出现Error: couldn't connect to server 127.0.0.1:27017 src/mongo/shell/mongo.js:84 错误；现在的解决方案输入如下命令（还没有根本解决）：
/usr/bin/mongod --dbpath=/opt/mongodb2.2.7/data --logpath=/opt/mongodb2.2.7/logs --logappend  --port=27017 --fork
	对原始opinion_news目录下文件 做了如下修改：
	添加requirements.txt文件，其中包括项目代码运行环境的信息，该文件必须在docker的根目录
	对/opinion_news/opinion 目录下__init__.py 文件删除下面一行
from flask_debugtoolbar import DebugToolbarExtension
	对/opinion_news/opinion_cal 目录下util.py 文件修改两个变量
MONGOD_HOST = ‘localhost’
MONGOD_PORT = 27017
	启动该服务命令
docker run -p 8080:9001 -i -t kmeans:4.2 python /opinion_news/run.py 

# docker仓库的镜像怎么删除

docker越来越炙手可热，如果你的团队已经准备开始使用docker，那么私有仓库是必不可少的东西，首先是可以帮助你加快从服务器pull镜像的速度，其次也可以帮助你存放私有的镜像，本文主要为大家介绍如何从公用服务器上讲开放的images备份到本地私有服务器上。
docker images往往不知不觉就占满了硬盘空间，为了清理冗余的image，可采用以下方法：

1.进入root权限

sudo su

2.停止所有的container，这样才能够删除其中的images：

docker stop $(docker ps -a -q)

如果想要删除所有container的话再加一个指令：

docker rm $(docker ps -a -q)

3.查看当前有些什么images

docker images

4.删除images，通过image的id来指定删除谁

docker rmi <image id>

想要删除untagged images，也就是那些id为<None>的image的话可以用

docker rmi $(docker images | grep "^<none>" | awk "{print $3}")

要删除全部image的话

docker rmi $(docker images -q)
