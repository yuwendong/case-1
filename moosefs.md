# MooseFS

## 1 参考资料
### 1.1 参考chenlijun evernote
https://www.evernote.com/shard/s442/sh/7553c5b5-56d6-4c38-a7f6-58215cd38e0d/3f5e37e962902489

### 1.2 参考MooseFS官方文档
参考资料列表
* http://www.moosefs.org/tl_files/manpageszip/moosefs-step-by-step-tutorial-cn-v.1.1.pdf
* https://github.com/linhaobuaa/case/blob/master/moosefs-step-by-step-tutorial-cn-v.1.1.pdf

## 2 服务器部署
### 2.1 概述
我们假定使用的主机 ip 地址分配如下：
* 主控服务器 Master server: 219.224.135.46
* 主控备份服务器 Metalogger server: 未配备
* 存储块服务器 Chunk servers: 219.224.135.45, 219.224.135.47, 219.224.135.48, 219.224.135.60, 219.224.135.126
* 客户端主机 clients: 219.224.135.x

### 2.2 主控服务器
* 修改/etc/hosts，增加下面一行
```
219.224.135.46 mfsmaster
```
* 启动mfsmaster 
```
/usr/sbin/mfsmaster start
```
* 查看集群监控信息：http://219.224.135.46:9425/mfs.cgi?CCdata=cpu§ions=IN

### 2.3 存储服务器
1、新磁盘分区格式化：对/dev/sdb采用ext3格式化，并进行mount，参考https://help.ubuntu.com/community/InstallingANewHardDrive
```
mkdir -p /mnt/mfschunks1
mount /dev/sdb
```
如果/dev/sdb没有进行格式化，用如下命令进行硬盘格式化，前提是/dev/sdb盘可以进行格式化
```
sudo mkfs -t ext3 /dev/sdb1
```

### 2.3 客户端主机
1、安装fuse
```
cd /usr/src/
wget http://iweb.dl.sourceforge.net/project/fuse/fuse-2.X/2.9.3/fuse-2.9.3.tar.gz
tar zxvf fuse-2.9.3.tar.gz
cd fuse-2.9.3/
./configure
make && make install
```

2、安装客户端软件 mfsmount
```
cd /usr/src/
wget http://pro.hit.gemius.pl/hitredir/id=.WCbG2t.7Ln5k1s3Q9xPg8cPfX.wVMc5kyXfrKcJTDH.c7/url=moosefs.org/tl_files/mfscode/mfs-1.6.27-5.tar.gz
tar zvxf mfs-1.6.27-5.tar.gz
cd mfs-1.6.27/
./configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var/lib --with-default-user=mfs  --with-default-group=mfs --disable-mfsmaster  --disable-mfschunkserver --enable-mfsmount
make && make install
```

3、修改文件/etc/hosts ，增加如下的文本行:
```
219.224.135.46 mfsmaster
```

4、假定客户端的挂接点是/mnt/mfs，我们将以下面的指令来使用 MooseFS 分布式共享文件系统:
* 创建挂接点
```
mkdir -p /mnt/mfs
```
* 开始挂接操作
```
/usr/bin/mfsmount /mnt/mfs -H mfsmaster
```

## 错误处理
### configure: error: zlib development library not found
```
wget http://zlib.net/zlib-1.2.8.tar.gz
./configure
make && make install
```



安装fuse最新版

在126上安装主控服务器 Master server
为了操作方便，切换到root用户
/etc/mfs/mfsexports.cfg
#*                      /       rw,alldirs,maproot=0
219.224.135.0/24        /       rw,alldirs,maproot=0

4，一切按照http://www.moosefs.org/tl_files/manpageszip/moosefs-step-by-step-tutorial-cn-v.1.1.pdf操作即可

5,可能会出现configure: error: zlib development library not found
/usr/src# wget http://zlib.net/zlib-1.2.8.tar.gz
./configure
make && make install

6, 按照https://help.ubuntu.com/community/InstallingANewHardDrive的建议准备分区的时候，
sudo fdisk /dev/sdb 会出现partition1已经存在的情况，直接用就好了,sudo mkfs -t ext3 /dev/sdb1
mkdir /mnt/mfschunks1
mount /dev/sdb1 /mnt/mfschunks1

修改chunkserver的挂载路径
vim mfshdd.cfg
/mnt/mfschunks1

7,安装mfs客户端
cd /usr/src/
wget http://iweb.dl.sourceforge.net/project/fuse/fuse-2.X/2.9.3/fuse-2.9.3.tar.gz
tar zxvf fuse-2.9.3.tar.gz
cd fuse-2.9.3/
./configure
make && make install

cd /usr/src/
tar zvxf zlib-1.2.8.tar.gz
cd zlib-1.2.8/
./configure
make && make install

cd /usr/src/
wget http://pro.hit.gemius.pl/hitredir/id=.WCbG2t.7Ln5k1s3Q9xPg8cPfX.wVMc5kyXfrKcJTDH.c7/url=moosefs.org/tl_files/mfscode/mfs-1.6.27-5.tar.gz
tar zvxf mfs-1.6.27-5.tar.gz
cd mfs-1.6.27/
./configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var/lib --with-default-user=mfs  --with-default-group=mfs --disable-mfsmaster  --disable-mfschunkserver --enable-mfsmount
make && make install

vi /etc/hosts
添加一行
219.224.135.126 mfsmaster
mkdir -p /mnt/mfs
/usr/bin/mfsmount /mnt/mfs -H mfsmaster

aclocal-1.14: command not found
LANG=C
sudo apt-get install intltool


续：
http://219.224.135.126:9425/mfs.cgi?CCdata=cpu§ions=IN监控信息
