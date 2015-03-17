
mysqldump -uroot -h219.224.135.46 weibo > weibo.sql

mysql -uroot -h219.224.135.47

CREATE DATABASE weibo DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

use weibo;

source weibo.sql;
