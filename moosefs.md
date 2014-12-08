
https://www.evernote.com/shard/s442/sh/7553c5b5-56d6-4c38-a7f6-58215cd38e0d/3f5e37e962902489

1，两台服务器信息
219.224.135.91
ubuntu6
Bhsem123456

219.224.135.60
ubuntu2
Bh123456
准备用126做主服务器，60做备份服务器

2，安装fuse最新版

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


续：
http://219.224.135.126:9425/mfs.cgi?CCdata=cpu§ions=IN监控信息


