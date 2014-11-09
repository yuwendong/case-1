1.ssh root@219.224.135.60 

cd /etc/mysql;

vim mysqld_multi.cnf
```
[mysqld_multi]
mysqld = /usr/bin/mysqld_safe
mysqladmin = /usr/bin/mysqladmin
#user = root

[mysqld1]
#user		= root
pid-file	= /var/run/mysqld/mysqld.pid
socket		= /var/run/mysqld/mysqld.sock
port		= 3306
datadir		= /var/lib/mysql
server_id 	= 108
bind_address	= 0.0.0.0

[mysqld2]
#user		= root
port		= 3307
socket		= /tmp/mysqld3307/mysqld.sock
pid-file 	= /tmp/mysqld3307/mysqld.pid
datadir 	= /var/lib/mysql3307
server-id 	= 109
bind_address	= 0.0.0.0

[mysqld3]
#user		= root
pid-file	= /tmp/mysqld3308/mysqld.pid
socket 		= /tmp/mysqld3308/mysqld.sock
port 		= 3308
datadir 	= /var/lib/mysql3308
server-id 	= 110
bind_address	= 0.0.0.0
```

2.mysqld_multi --defaults-extra-file=/etc/mysql/mysqld_multi.cnf report




