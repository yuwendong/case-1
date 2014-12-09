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
