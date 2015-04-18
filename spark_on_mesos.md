配置spark的mesos模式

一、Mesos配置
```
master：219.224.135.46，
slave：219.224.135.47，219.224.135.48，219.224.135.60
```

1.配置master到slave服务器的无密码ssh登陆

现在确认能否不输入口令就用ssh登录localhost:
```
$ ssh localhost
```

如果不输入口令就无法用ssh登陆localhost，执行下面的命令：
```
$ ssh-keygen -t dsa -P '' -f ~/.ssh/id_dsa 
$ cat ~/.ssh/id_dsa.pub >> ~/.ssh/authorized_keys
```
至此免密码ssh登陆localhost配置完成

```
$ scp ~/.ssh/id_dsa.pub root@219.224.135.47:~/.ssh/authorized_keys
$ scp ~/.ssh/id_dsa.pub root@219.224.135.48:~/.ssh/authorized_keys
$ scp ~/.ssh/id_dsa.pub root@219.224.135.60:~/.ssh/authorized_keys
```
至此master到各个slave的免密码ssh登陆配置完成

2.配置mesos

统一安装位置：/home/spark/
参见http://mesos.apache.org/gettingstarted/
尽量使用Apache官网下载方案，git版本不稳定

安装结束后，查看/etc/ld.so.conf，加入下面一行，若已存在则忽略这步。
```
/usr/local/lib
```
执行ldconfig -v，使生效。
mesos启动后可通过219.224.135.46:5050查看Web UI界面

二、Spark配置

1.获取spark

可直接从46服务器上获取spark编译包
```
$ cd /home/spark
$ scp -r spark-1.0.1-bin-hadoop1 root@219.224.135.47:/home/spark/
$ scp -r spark-1.0.1-bin-hadoop1 root@219.224.135.48:/home/spark/
$ scp -r spark-1.0.1-bin-hadoop1 root@219.224.135.60:/home/spark/
```
注意，修改spark包中的代码时只需在46服务器上修改，之后将修改后的代码分发到另外3台服务器上，保持代码的一致性。

2.配置spark运行模式

参考http://spark.apache.org/docs/latest/cluster-overview.html

注意配置Mesos模式时，在conf/spark-env.sh中

```
MESOS_NATIVE_LIBRARY=/usr/local/lib/libmesos.so
```

3.配置pyspark包
```
$ cd /home/spark/spark-1.0.1-bin-hadoop1/python
$ cp -r pyspark /usr/lib/python2.7/
```
4.配置环境变量

```
$ vim /etc/environment
```
添加以下内容
```
SPARK_HOME=/home/spark/spark-1.0.1-bin-hadoop1
```
执行以下命令，重新登陆服务器后，修改生效
```
$ source /etc/environment
```


三、可能遇到的问题

１.编译mesos时可能会遇到could not find the main class: org.codehaus.plexus.classworlds.launcher.Launcher. Program will exit，原因是maven环境没有配置好

配置maven环境变量
在/etc/environment中添加以下语句：
```
$ M2_HOME=/usr/share/maven
$ M2=/usr/share/maven/bin
```
在命令行输入以下语句，并重新登录服务器，使修改生效
```
$ source /etc/environment
```
输入以下命令检查maven是否配置完成
```
$ mvn -version
```
若仍有错误，则java配置有问题，继续执行以下步骤。
将当前机器java版本设置成java-7-oracle，参考http://www.linuxdiyf.com/linux/2788.html
若未安装java7则进行安装
```
$ sudo apt-get install python-software-properties
$ sudo add-apt-repository ppa:webupd8team/java
$ sudo apt-get update
$ sudo apt-get install oracle-jdk7-installer
```
并在/etc/environment中添加环境变量，重新登录后生效
```
$ CLASSPATH=/usr/lib/jvm/java-7-oracle/lib
$ JAVA_HOME=/usr/lib/jvm/java-7-oracle
```

2.E: Sub-process /usr/bin/dpkg returned an error code (1)
参考http://bbs.ednchina.com/BLOG_ARTICLE_3010256.HTM

3.no space on device
参考http://blog.csdn.net/pang040328/article/details/40041821

4.ubuntu encountered a section with no package header
参考http://blog.csdn.net/hs794502825/article/details/7835902

５.cannot locate package
先检查package名字是否输入错误(注意字母l和数字1）
```
sudo apt-get update
```

6.初始化月份字符串错误error initializing month string
参考http://blog.csdn.net/plunger2011/article/details/25806133

四、mesos启动

参考http://mesos.apache.org/documentation/latest/deploy-scripts/

1.集群启动

登陆master节点（219.224.135.46）
可以在/usr/local/var/mesos/deploy/下配置环境变量
```
$ cd /usr/local/sbin
$ ./mesos-start-cluster.sh
```
2.集群停止

登陆master节点（219.224.135.46）
```
$ cd /usr/local/sbin
$ ./mesos-stop-cluster.sh
```
3.webUI界面
219.224.135.46:5050
