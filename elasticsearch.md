内存和打开的文件数 
如果你的elasticsearch运行在专用服务器上，经验值是分配一半内存给elasticsearch。另一半用于系统缓存，这东西也很重要的。 你可以通过修改ES_HEAP_SIZE环境变量来改变这个设定。在启动elasticsearch之前把这个变量改到你的预期值。另一个选择上球该elasticsearch的ES_JAVA_OPTS变量，这个变量时在启动脚本(elasticsearch.in.sh或elasticsearch.bat)里传递的。你必须找到-Xms和-Xmx参数，他们是分配给进程的最小和最大内存。建议设置成相同大小。嗯，ES_HEAP_SIZE其实就是干的这个作用。 

你必须确认文件描述符限制对你的elasticsearch足够大，建议值是32000到64000之间。关于这个限制的设置，另有教程可以参见。 

Everything works great until I run an agg search, then shards start failing with: "java.lang.OutOfMemoryError: Java heap space"

I have changed heap size with: export ES_HEAP_SIZE=16g (also ES_MAX_MEM and ES_MIN_MEM to same)

also chaged the yml file for elasticsearch: bootstrap.mlockall: true

and even (recommended by install documents): sudo sysctl -w vm.max_map_count=262144

Restart service and still no no impact, still "java.lang.OutOfMemoryError: Java heap space"

```
PUT /_river/guba_post/_meta
{
  "type": "mongodb",
  "mongodb": { 
    "servers":
    [
      { "host": "219.224.135.47", "port": "27019" }
    ],
    "db": "guba", 
    "collection": "post"
  }, 
  "index": { 
    "name": "guba",
    "type": "post"
  }
}

PUT /_river/guba_stock/_meta
{
  "type": "mongodb",
  "mongodb": { 
    "servers":
    [
      { "host": "219.224.135.47", "port": "27019" }
    ],
    "db": "guba", 
    "collection": "stock"
  }, 
  "index": { 
    "name": "guba",
    "type": "stock"
  }
}

PUT _template/template_master_timeline_user/
{
    "template": "master_timeline_user",
    "order": 0,
    "mappings": {
        "user": {
            "properties": {
                "name": {
                    "type": "string",
                    "index": "not_analyzed"
                }
            }
        }
    }
}

PUT /_river/test_river_master_timeline_weibo_topic_545f4c22cf198b18c57b8014/_meta
{
  "type": "mongodb",
  "mongodb": { 
    "servers":
    [
      { "host": "219.224.135.47", "port": "27019" }
    ],
    "db": "54api_weibo_v2", 
    "collection": "master_timeline_weibo_topic_545f4c22cf198b18c57b8014"
  }, 
  "index": { 
    "name": "master_timeline_weibo_topic",
    "type": "545f4c22cf198b18c57b8014"
  }
}

PUT /_river/test_river_master_timeline_user/_meta
{
  "type": "mongodb",
  "mongodb": { 
    "servers":
    [
      { "host": "219.224.135.47", "port": "27019" }
    ],
    "db": "54api_weibo_v2", 
    "collection": "master_timeline_user"
  }, 
  "index": { 
    "name": "master_timeline_user",
    "type": "user"
  }
}

PUT /_river/test_river_master_timeline_weibo_topic_545f2cbecf198b18c57b8013/_meta
{
  "type": "mongodb",
  "mongodb": { 
    "servers":
    [
      { "host": "219.224.135.47", "port": "27019" }
    ],
    "db": "54api_weibo_v2", 
    "collection": "master_timeline_weibo_topic_545f2cbecf198b18c57b8013"
  }, 
  "index": { 
    "name": "master_timeline_weibo_topic",
    "type": "545f2cbecf198b18c57b8013"
  }
}

PUT /_river/test_river_master_timeline_weibo_topic_5460e65501d4a554d8b00894/_meta
{
  "type": "mongodb",
  "mongodb": { 
    "servers":
    [
      { "host": "219.224.135.47", "port": "27019" }
    ],
    "db": "54api_weibo_v2", 
    "collection": "master_timeline_weibo_topic_5460e65501d4a554d8b00894"
  }, 
  "index": { 
    "name": "master_timeline_weibo_topic",
    "type": "5460e65501d4a554d8b00894"
  }
}
```
