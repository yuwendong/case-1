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
同理在26,27上分别创建上述文件目录

3.2 replication sets
1）创建replication set1：rs0
219.224.135.46:
```
cd /home/mongodb/mongodb-linux-x86_64-2.6.4/bin
```
创建replication set:rs0
```
numactl --interleave=all ./mongod --port=27017 --replSet=rs0 --dbpath=/var/lib/mongodb_rs0 --logpath=/var/log/mongodb/mongodb.log --logappend --fork --smallfiles
```
创建成功会有如下说明：
```
child process started successfully, parent existing
```
在47上做如上操作
初始化replication set1:rs0
使用mongo进入一个mongod
```
mongo --port 27017 --host 219.224.135.46
rs.initiate();

```
****需要再确定一下****
2）创建replication set:rs1
在219.224.135.45和219.224.135.48:
```
cd /home/mongodb/mongodb-linux-x86_64-2.6.4/bin
```
创建replication set：rs1
```
numactl --interleave=all ./mongod --port=27017 --replSet=rs1 --dbpath=/var/lib/mongodb_rs1 --logpath=/var/log/mongodb/mongodb.log --logappend --fork --smallfiles
```

3.3 config server
3.4 mongos
3.5 shard cluster
3.6 collection

##4 相关问题
