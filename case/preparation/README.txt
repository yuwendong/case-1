微博用户数据准备:

   a.收集爬虫数据

     a1. 在各台机器上启动mongodb，进入各台机器的mongodb源码路径，执行如下命令：

     cd $MONGODB_PATH/bin

     numactl --interleave=1 ./mongod --dbpath=/var/lib/mongodb --logpath=/var/log/mongodb/mongodb.log --logappend --fork

     各台机器的IP和MONGODB_PATH:

     219.224.135.46	/opt/mongodb/mongodb-linux-x86_64-2.2.2
     219.224.135.61	/home/arthas/Downloads/mongodb-linux-x86_64-2.2.4

     a2. 将mongodb的用户数据导出到本地bson文件：

     mongodump -u root -p root -d master_timeline_v1 -c master_timeline_user -o /home/arthas/linhao/

     219.224.135.46: mongodump -u root -p root -d master_timeline -c master_timeline_user -o /home/arthas/linhao/

     a3. 将本地bson文件传输到目标服务器的case/data/master_timeline_user_bson/路径下：

     rsync -r master_timeline_v1 --progress root@219.224.135.47:/home/ubuntu3/linhao/case/data/master_timeline_user_bson/

  b. 解析bson文件为json格式数据

     b1. 安装xapian_case, 因为xapian_case.bs_input被调用

     b2. 错误: from bson import InvalidBsonInput, no moduled name InvalidBsonInput
         解决方案：将package_install/pymongo-2.4.2-py2.7-linux-x86_64.tar.gz解压为
                     pymongo-2.4.2-py2.7-linux-x86_64.egg
                     放入/usr/local/lib/python2.7/dist-packages, 删除dist-packages下的bson包

     b3. 在consts.py文件中设置相关参数,运行userBson2json.py
