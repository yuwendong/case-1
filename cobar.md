
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
sudo apt-get install mysql-server
```

2. cobar配置

cobar_server: 219.224.135.46

cobar 装在219.224.135.46 /home/cobar/cobar-server-1.2.7/路径，启动命令：bin/startup.sh

conf/schema.xml
```
   <!-- schema定义 -->                                                       
 21   <schema name="production_cobar_schema" dataNode="dnTest2">                
 22     <table name="test" dataNode="dnTest1,dnTest2,dnTest3,dnTest4,dnTest5,dnTest6" r❯
 23   </schema>                                                                 
 24                                                                             
 25   <!-- 数据节点定义，数据节点由数据源和其他一些参数组织而成。-->            
 26   <dataNode name="dnTest1">                                                 
 27     <property name="dataSource">                                            
 28       <dataSourceRef>dsTest[0]</dataSourceRef>                              
 29     </property>                                                             
 30   </dataNode>                                                               
 31   <dataNode name="dnTest2">                                                 
 32     <property name="dataSource">                                            
 33       <dataSourceRef>dsTest[1]</dataSourceRef>                              
 34     </property>                                                             
 35   </dataNode>                                                               
 36   <dataNode name="dnTest3">                                                 
 37     <property name="dataSource">
 38       <dataSourceRef>dsTest[2]</dataSourceRef>                              
 39     </property>                                                             
 40   </dataNode>                                                               
 41   <dataNode name="dnTest4">                                                 
 42     <property name="dataSource">                                            
 43       <dataSourceRef>dsTest[3]</dataSourceRef>                              
 44     </property>                                                             
 45   </dataNode>                                                               
 46   <dataNode name="dnTest5">                                                 
 47     <property name="dataSource">                                            
 48       <dataSourceRef>dsTest[4]</dataSourceRef>                              
 49     </property>                                                             
 50   </dataNode>                                                               
 51   <dataNode name="dnTest6">                                                 
 52     <property name="dataSource">                                            
 53       <dataSourceRef>dsTest[5]</dataSourceRef>                              
 54     </property>                                                             
 55   </dataNode>
 56
  57   <!-- 数据源定义，数据源是一个具体的后端数据连接的表示。-->                
 58   <dataSource name="dsTest" type="mysql">                                   
 59     <property name="location">                                              
 60       <location>219.224.135.45:3306/weibo</location>                        
 61       <location>219.224.135.46:3306/weibo</location>                        
 62       <location>219.224.135.47:3306/weibo</location>                        
 63       <location>219.224.135.48:3306/weibo</location>                        
 64       <location>219.224.135.60:9001/weibo</location>                        
 65       <location>219.224.135.126:3306/weibo</location>                       
 66     </property>                                                             
 67     <property name="user">root</property>                                   
 68     <property name="password"></property>                                   
 69     <property name="sqlMode">STRICT_TRANS_TABLES</property>                 
 70   </dataSource>
 ```
 
 server.xml
 ```
    <!-- 用户访问定义，用户名、密码、schema等信息。 -->                       
 37   <user name="root">                                                        
 38     <property name="password"></property>                                   
 39     <property name="schemas">production_cobar_schema</property>             
 40   </user>                                                                   
 41   <!--
 ```
 
 rule.xml
 ```
 20   <!-- 路由规则定义，定义什么表，什么字段，采用什么路由算法 -->             
 21   <tableRule name="rule1">                                                  
 22     <rule>                                                                  
 23       <columns>id</columns>                                                 
 24       <algorithm><![CDATA[ func1(${id}) ]]></algorithm>                     
 25     </rule>                                                                 
 26   </tableRule>                                                              
 27                                                                             
 28   <!-- 路由函数定义 -->                                                     
 29   <function name="func1" class="com.alibaba.cobar.route.function.PartitionB❯
 30     <property name="partitionCount">6</property>                            
 31     <property name="partitionLength">170</property>                         
 32   </function> 
 ```
 
 注:
 
 a. 如果schema中定义的table是每个mysql实例分别建的，那么如果6个节点的mysql实例中其中有一个实例没建该表，会报错
 
 b. 

