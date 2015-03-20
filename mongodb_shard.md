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
126,60————shard3(rs2)
replication sets:（45,48），（46,47）,(126,60)一主一从即primary，secondary
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
同理在46,47,48,126,60上分别创建上述文件目录

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
numactl --interleave=all ./mongod --port=27017 --replSet=rs0 --dbpath=/var/lib/mongodb_rs0 --logpath=/var/log/mongodb/mongodb.log --logappend --fork --smallfiles
```
--rest表示可以通过host:28017在浏览器中管理mongodb实例
--auth表示连接时的安全性验证
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

3）创建replication set:rs2
在219.224.135.126和219.224.135.60:
```
cd /home/mongodb/mongodb-linux-x86_64-2.6.4/bin
```
创建replication set：rs2
```
numactl --interleave=all ./mongod --port=27017 --replSet=rs2 --dbpath=/var/lib/mongodb_rs2 --logpath=/var/log/mongodb/mongodb.log --logappend --fork --smallfiles
```
初始化replication set3：rs2
使用mongo进入一个primary mongod
```
mongo --port 27017 --host219.224.135.126
rs.initiate();
rs.add('219.224.135.60');
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
>db.runCommand({addshard:'rs0/mirage:27017,219.224.135.47:27017'}); 
#这里可能会出现问题，由于在设置replication #set时primary节点的host默认为用户名，而不是ip。这个可以通过rs.status();进行查看
>db.runCommand({addshard:'rs1/219.224.135.45:27017,ubuntu4:27017'});
>db.runCommand({addshard:'rs2/ubuntu5:27017,219.224.135.60:27017'});
```
在添加了shards之后，查看是否配置成功
```
>db.runCommand({listshards:1})
{
	"shards" : [
		{
			"_id" : "rs1",
			"host" : "rs1/219.224.135.45:27017,ubuntu4:27017"
		},
		{
			"_id" : "rs0",
			"host" : "rs0/219.224.135.47:27017,mirage:27017"
		},
		{
			"_id" : "rs2",
			"host" : "rs2/219.224.135.60:27017,ubuntu5:27017"
		}
	],
	"ok" : 1
}
```
激活数据库分片：
```
>db.runCommand({enablesharding:'54api_weibo_v2'});
>db.runCommand({enablesharding:'boat'});
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
>db.runCommand({shardcollection:'boat.boatcol',key:{'id':'hashed'}});
>db.runCommand({shardcollection:'54api_weibo_v2.master_timeline_user',key:{'id':'hashed'}});
```
查看配置情况：
```
use 54api_weibo_v2
mongos> db.stats()
{
	"raw" : {
		"rs0/219.224.135.47:27017,mirage:27017" : {
			"db" : "54api_weibo_v2",
			"collections" : 288,
			"objects" : 7259812,
			"avgObjSize" : 2536.4785666626076,
			"dataSize" : 18414357536,
			"storageSize" : 25148407792,
			"numExtents" : 2647,
			"indexes" : 557,
			"indexSize" : 547203328,
			"fileSize" : 26813923328,
			"nsSizeMB" : 16,
			"dataFileVersion" : {
				"major" : 4,
				"minor" : 5
			},
			"extentFreeList" : {
				"num" : 0,
				"totalSize" : 0
			},
			"ok" : 1
		},
		"rs1/219.224.135.45:27017,ubuntu4:27017" : {
			"db" : "54api_weibo_v2",
			"collections" : 273,
			"objects" : 6554653,
			"avgObjSize" : 2768.4976324452264,
			"dataSize" : 18146541312,
			"storageSize" : 22381359104,
			"numExtents" : 2528,
			"indexes" : 542,
			"indexSize" : 544374432,
			"fileSize" : 24130879488,
			"nsSizeMB" : 16,
			"dataFileVersion" : {
				"major" : 4,
				"minor" : 5
			},
			"extentFreeList" : {
				"num" : 3,
				"totalSize" : 293744640
			},
			"ok" : 1
		}
	},
	"objects" : 13814465,
	"avgObjSize" : 2646.0787830726704,
	"dataSize" : 36560898848,
	"storageSize" : 47529766896,
	"numExtents" : 5175,
	"indexes" : 1099,
	"indexSize" : 1091577760,
	"fileSize" : 50944802816,
	"extentFreeList" : {
		"num" : 3,
		"totalSize" : 293744640
	},
	"ok" : 1
}
mongos> db.boatcol.getShardDistribution()

Shard rs1 at rs1/219.224.135.45:27017,ubuntu4:27017
 data : 54.14Mb docs : 31377 chunks : 1
 estimated data per chunk : 54.14Mb
 estimated docs per chunk : 31377

Totals
 data : 54.14Mb docs : 31377 chunks : 1
 Shard rs1 contains 100% data, 100% docs in cluster, avg obj size on shard : 1kb

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

mongodb修改最大连接数参考http://blog.163.com/ji_1006/blog/static/1061234120121120114047464/

4)重要：MongoDB要求文件系统对目录支持fsync()。所以例如HGFS和Virtual Box的共享目录不支持这个操作。
　　
　推荐配置
　
　a. 在包含数据文件的卷关闭atime配置。
　
　b. 按照UNIX ulimit设置的推荐，设置描述符限制，-n及其他用户进程限制(ulimit)，-u到多于20000。较低的ulimit配置在大压力情况下会影响MongoDB，并且可能产生错误及导致连接到MongoDB失败和服务不可用。
　
　c. 不要使用hugepages虚拟内存页，因为MongoDB在正常虚拟内存页中表现更好。
　
　d. 在BIOS中禁用NUMA。如果做不到，请参考MongoDB和NUMA硬件章节。
　
　e. 确保存放数据文件的块设备的readahead配置合理。对随机访问模式，设置较低的readahead值。readahead 32(或16kb)通常工作良好。
　　
　f. 使用网络时间协议(NTP)保证服务器间的时间同步。这对于分片集群来说尤其重要。
　
(5)服务器时间同步

```
ntpdate cn.pool.ntp.org
date
hwclock
hwclock --localtime
hwclock --utc
hwclock -w 
sudo apt-get install ntp
```
参考http://blog.sina.com.cn/s/blog_636a55070101u1mg.html，http://wiki.ubuntu.org.cn/NTP

(6) "errmsg" : "please create an index that starts with the shard key before sharding."
use boat
db.boat.ensureIndex({"id": "hashed"})

(7) mongodump 备份 与 mongorestore 恢复
```
cd /home/ubuntu3/linhao/mongodump/
mongodump --host 219.224.135.46 --port 27019 -d news -o ./
mongorestore --host 219.224.135.92 --db news --directoryperdb news/
mongodump --host 219.224.135.46 --port 27019 -d 54api_weibo_v2 -o ./
mongorestore --host 219.224.135.92 --db news --directoryperdb 54api_weibo_v2/
```
