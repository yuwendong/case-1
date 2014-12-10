配置spark的mesos模式

Mesos配置
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

配置完成后可将mesos文件夹分发到其他服务器相同位置下，无需单独进行make，make install

