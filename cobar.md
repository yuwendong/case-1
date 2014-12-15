
cobar_server: 219.224.135.46

参考资料：https://github.com/alibaba/cobar/wiki

1. Mysql 配制

error:host is not allowed to connect to mysql server

允许root使用密码从任何主机连接到mysql服务器：
```
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '' WITH GRANT OPTION;
```

 mysql -uroot -h219.224.135.45、46、47、48、126
CREATE DATABASE weibo DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

mysql -u root -h219.224.135.46 -P8066
```
mysql> show databases;
+-------------------------+
| DATABASE                |
+-------------------------+
| production_cobar_schema |
+-------------------------+
1 row in set (0.04 sec)
mysql> show cobar_status;
+--------+
| STATUS |
+--------+
| ON     |
+--------+
1 row in set (0.01 sec)
```

彻底重装mysql
```
sudo apt-get purge mysql-server-5.1 mysql-common
```
