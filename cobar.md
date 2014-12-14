
cobar_server: 219.224.135.46

参考资料：https://github.com/alibaba/cobar/wiki

error:host is not allowed to connect to mysql server

允许root使用密码从任何主机连接到mysql服务器：
```
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '' WITH GRANT OPTION;
```
