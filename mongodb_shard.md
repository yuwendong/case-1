#mongodb_shard安装配置

##1 mongodb源码安装
创建mongodb用户
```
adduser mongodb
```
在/home/mongodb/下载mongodb源码，并进行解压，生成文件夹mongodb-linux-x86_64-2.6.4

```
    tar zxvf mongodb-linux-x86_64-1.6.2.tgz
```


##2 mongodb_shard结构说明
本次配置涉及到4台服务器，45，46，47，48，构成2个shard
需要存在的结构：replication sets，mongod，mongod config sever，mongos。
45,48————shard1（rs0）
46,47————shard2（rs1）
replication sets:（45,48），（46,47）一主一从即primary，secondary
mongod config sever:46,47,48
mongos:46,47,48

##3 具体配置
3.1 创建文件目录
219.224.135.45
```
mkdir /var/lib/mongodb_rs0
mkdir /var/lib/mongodb_rs1
mkdir /var/log/mongodb
```
同理在46,47,48上分别创建上述文件目录

219.224.135.46
```
mkdir /var/lib/mongodb_config_server
```
同理在47,48上创建config server的文件夹
3.2 replication sets
1）创建replication set1：rs0
219.224.135.46:
```
cd /home/mongodb/mongodb-linux-x86_64-2.6.4/bin
```
创建replication set:rs0
```
numactl --interleave=all ./mongod --port=27017 --replSet=rs0 --dbpath=/var/lib/mongodb_rs0 --logpath=/var/log/mongodb/mongodb.log --logappend --fork --smallfiles --rest
```
--rest表示可以通过host:28019在浏览器中管理mongodb实例
创建成功会有如下说明：
```
child process started successfully, parent existing
```
在47上做如上操作
初始化replication set1:rs0
使用mongo进入一个primary mongod
```
mongo --port 27017 --host 219.224.135.46
rs.initiate();
rs.add('219.224.135.47');
rs.status();    #查看replication set的状态
```

2）创建replication set:rs1
在219.224.135.45和219.224.135.48:
```
cd /home/mongodb/mongodb-linux-x86_64-2.6.4/bin
```
创建replication set：rs1
```
numactl --interleave=all ./mongod --port=27017 --replSet=rs1 --dbpath=/var/lib/mongodb_rs1 --logpath=/var/log/mongodb/mongodb.log --logappend --fork --smallfiles
```
初始化replication set2：rs1
使用mongo进入一个primary mongod
```
mongo --port 27017 --host219.224.135.48
rs.initiate();
rs.add('219.224.135.45');
rs.status();
```

3.3 config server
分别在46,47,48上作如下配置：
```
cd /home/mongodb/mongodb-linux-x86_64-2.6.4/bin
./mongod --configsvr --dbpath /var/lib/mongodb_config --port 27018 --logpath /var/log/mongodb/config.log --logappend --fork
```

3.4 mongos
在46,47,48config server上分别执行：
```
cd /home/mongodb/mongodb-linux-x86_64-2.6.4/bin
./mongos --configdb 219.224.135.46:27018,219.224.135.47:27018,219.224.135.48:27018 --port 27019 --logpath /var/log/mongodb/mongos.log --logappend --fork
```

3.5 shard cluster
连接到其中一个mongos进程，并切换到admin数据库进行如下配置：
```
mongo --port 27019 --host 219.224.135.46
>use admin;
>db.runCommand({addshard:'rs0/219.224.135.46:27017,219.224.135.47:27017'}); 
#这里可能会出现问题，由于在设置replication #set时primary节点的host默认为用户名，而不是ip。这个可以通过rs.status();进行查看
>db.runCommand({addshard:'rs1/219.224.135.45:27017',219.224.135.48:27017});
```
在添加了shards之后，查看是否配置成功
```
>db.runCommand({listshards:1})
```
激活数据库分片：
```
>db.runCommand({enablesharding:'54api_weibo_v2'});
```
查看数据库分片是否成功：
```
sh.status();
```
查看对应的database对应的partitioned是否为'true'
3.6 collection
同上也是在mongos中进行配置
```
>db.runCommand({shardcollection:'54api_weibo_v2.master_timeline_user',key:{id:'hashed'}});
>db.runCommand({shardcollection:'54api_weibo_v2.master_timeline_weibo',key:{id:'hashed'}});
```
查看配置情况：
```
sh.stats();
```
查看'raw'是否有'rs0','rs1'的相关信息

##4 相关问题
1)在进入mongo时出现问题，使用以下语句：
```
export LC_ALL='C'
```
2)在添加shard后一定要启动对应数据库的shard，即enablesharding。
否则在此后的collection中，不能成功给collection分片

3)/var/log/mongodb/config.log
accept() returns -1 errno:24 Too many open files

solution: vim /etc/bash.bashrc
ulimit -n 65536
source /etc/bash.bashrc
