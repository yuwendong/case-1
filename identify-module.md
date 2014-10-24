#Identify-module 安装配置

##1.功能说明

该模块即网络分析模块，主要有两部分组成：case/cron/identify,case/identify。
前者完成了计算pagerank，degreerank方法以及生成网络图gexf。
后者完成对SSDB中图数据的查询及返回前端的功能。

##2.安装配置

###2.1 安装HAT

```
    git clone https://github.com/linhaobuaa/hat.git
```

###2.2 安装lxml

在安装lxml之前要先安装libxml2,libxlt.

```
    sudo apt-get install libxml2
    sudo apt-get install libxlt1-dev
    easy_install lxml
```

###2.3 安装SSDB

安装
```
    wget --no-check-certificate https://github.com/ideawu/ssdb/archive/master.zip
    unzip master
    cd ssdb-master
    make
    sudo make install

```
启动
```
    cd /home/ubuntu3/huxiaoqian/ssdb-master/
    
    # start master
    ./ssdb-server ssdb.conf

    # or start as daemon
    ./ssdb-server -d ssdb.conf
    
    # 停止 ssdb-server
    kill `cat ./var/ssdb.pid`
```
配置
```
    cd /usr/local/ssdb/ssdb.cli
    vim ssdb.conf
    将该文件中的ip改为0.0.0.0
```
###2.4 安装networkx
```
    sudo pip install networkx
```
注意：若该步骤出现问题，先确定是否安装了setuptools
```
    wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo python
```
另，networks的使用可能还需要安装numpy
```
    sudo apt-get install python-numpy
```

###2.5 安装Hadoop
