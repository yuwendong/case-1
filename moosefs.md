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
* 主控服务器 Master server: 219.224.135.47
* 主控备份服务器 Metalogger server: 未配备
* 存储块服务器 Chunk servers: 219.224.135.45, 219.224.135.47, 219.224.135.48, 219.224.135.60, 219.224.135.126
* 客户端主机 clients: 219.224.135.x

### 2.2 主控服务器
* 修改/etc/mfs/mfsexports.cfg
```
#*                      /       rw,alldirs,maproot=0
219.224.135.0/24        /       rw,alldirs,maproot=0
```

* 修改/etc/hosts，增加下面一行
```
219.224.135.47 mfsmaster
```
* 启动mfsmaster 
```
/usr/sbin/mfsmaster start
```
* 为了监控 MooseFS 当前运行状态，我们可以运行 CGI 监控服务，这样就可以用浏览器查看整个
MooseFS 的运行情况:
```
/usr/sbin/mfscgiserv
```
* 查看集群监控信息：http://219.224.135.47:9425/

### 2.3 存储服务器
1、使用新的整块磁盘做chunkserver的存储，新磁盘分区格式化：对/dev/sdb采用ext3格式化，并进行mount，参考https://help.ubuntu.com/community/InstallingANewHardDrive
```
mkdir -p /mnt/mfschunks1
mount /dev/sdb
```
如果/dev/sdb没有进行格式化，用如下命令进行硬盘格式化，前提是/dev/sdb盘可以进行格式化
```
sudo mkfs -t ext3 /dev/sdb1
```

2、修改chunkserver的挂载路径
```
vim /etc/mnt/mfshdd.cfg
/mnt/mfschunks1
```

3、在启动 chunk server 前，需确保用户 mfs 有权限读写将要被挂接的分区（因为 chunk server 运
行时要在此创建一个.lock 的文件）：
```
chown -R mfs:mfs /mnt/mfschunks1
```

4、类似地，修改/etc/hosts 文件，增加下面的行：
```
219.224.135.47 mfsmaster
```

5、开始启动 chunk server:
```
/usr/sbin/mfschunkserver start
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
219.224.135.47 mfsmaster
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
* 成功挂载
```
root@ubuntu5:/mnt/mfs# /usr/bin/mfsmount /mnt/mfs -H mfsmaster
mfsmaster accepted connection with parameters: read-write,restricted_ip ; root mapped to root:root
```

## 3 错误处理
### 3.1 configure: error: zlib development library not found
```
wget http://zlib.net/zlib-1.2.8.tar.gz
./configure
make && make install
```

### 3.2 can't open metadata file
/usr/sbin/mfsmaster start启动失败问题如下
```
root@mirage:~# /usr/sbin/mfsmaster start
working directory: /var/lib/mfs
lockfile created and locked
initializing mfsmaster modules ...
loading sessions ... ok
sessions file has been loaded
exports file has been loaded
mfstopology configuration file (/etc/mfstopology.cfg) not found - using defaults
loading metadata ...
can't open metadata file
if this is new instalation then rename /var/lib/mfs/metadata.mfs.empty as /var/lib/mfs/metadata.mfs
init: file system manager failed !!!
error occured during initialization - exiting
```

解决方案：重建meta数据
```
/usr/sbin/mfsmetarestore -a
```

### 3.3 aclocal-1.14: command not found
```
LANG=C
sudo apt-get install intltool
```

### 3.4 fuse: mountpoint is not empty
/usr/bin/mfsmount /mnt/mfs -H mfsmaster问题如下
```
root@ubuntu4:/mnt/mfs# /usr/bin/mfsmount /mnt/mfs -H mfsmaster
mfsmaster accepted connection with parameters: read-write,restricted_ip ; root mapped to root:root
fuse: mountpoint is not empty
fuse: if you are sure this is safe, use the 'nonempty' mount option
error in fuse_mount
```

解决方案如下
```
umount /mnt/mfs
```
