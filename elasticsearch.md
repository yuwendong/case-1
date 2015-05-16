限制内存使用

为了让聚集(或者任何需要访问字段值的请求)能够快点，访问fielddata一定会快些， 这就是为什么它加载到内存的原因。但是加载太多的数据到内存会导致垃圾回收缓慢， 因为JVM试着发现堆里面的额外空间，甚至导致OutOfMemory异常。

可能让你吃惊的是，你会发现Elaticsearch不是只把符合你的查询的值加载到fielddata. 而是把index里的所有document都加载到内存，甚至是不同的 _type 的document。

逻辑是这样的，如果你在这个查询需要访问documents X，Y和Z， 你可能在下一个查询 就需要访问别的documents。而一次把所有的值都加载并 保存在内存 ， 比每次查询 都去扫描倒排索引要更方便。

JVM堆是一个有限制的资源需要聪明的使用。有许多现存的机制去限制fielddata对堆内 存使用的影响。这些限制非常重要，因为滥用堆将会导致节点的不稳定（多亏缓慢的垃 圾回收）或者甚至节点死亡（因为OutOfMemory异常）。

选择一个堆大小
对于环境变量 $ES_HEAP_SIZE 在设置Elasticsearch堆大小的时候有2个法则可以运用:

不超过RAM的50%

Lucene很好的利用了文件系统cache，文件系统cache是由内核管理的。如果没有足够的文 件系统cache空间，性能就会变差。

不超过32G

如果堆小于32GB，JVM能够使用压缩的指针，这会节省许多内存：每个指针就会使用4字节 而不是8字节。

把对内存从32GB增加到34GB将意味着你将有 更少 的内存可用，因为所有的指针占用了 双倍的空间。同样，更大的堆，垃圾回收变得代价更大并且可能导致节点不稳定。

这个限制对大内存的影响主要是fielddata

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


DELETE guba

DELETE _river/test_river_guba

PUT /_river/test_river_guba_post/_meta
{
  "type": "mongodb",
  "mongodb": { 
    "servers":
    [
      { "host": "219.224.135.46", "port": "27019" }
    ],
    "db": "guba", 
    "collection": "stock"
  }, 
  "index": { 
    "name": "guba",
    "type": "stock"
  }
}

PUT /_river/test_river_guba/_meta
{
  "type": "mongodb",
  "mongodb": { 
    "servers":
    [
      { "host": "219.224.135.46", "port": "27019" }
    ],
    "db": "guba", 
    "collection": "post"
  }, 
  "index": { 
    "name": "guba",
    "type": "post"
  }
}

GET _river/_search

GET guba/post/_search

GET /_river/test_river_guba/_meta


GET guba/post/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "term": {
            "sentiment": 1
          }
        },
        {
          "term": {
            "has_sentiment": 1
          }
        },
        {
          "term": {
            "ad": 1
          }
        },
        {
          "range": {
            "releaseTime": {
              "gte": "2014-10-01 11:00:00",
              "lte": "2014-10-22 13:30:00"
            }
          }
        }
      ]
    }
  },
  "aggs": {
    "clicks_sum": {
      "sum": {
        "field": "clicks"
      }
    }
  }
}

DELETE /_template/template_guba

PUT /_template/template_guba
{
  "template": "guba",
  "order": 0,
  "settings": {
    "number_of_shards": 3
  },
  "mappings": {
    "post": {
      "properties": {
        "releaseTime": {
          "type": "date",
          "format": "yyyy-MM-dd HH:mm:ss"
        }
      }
    }
  }
}

PUT /_template/template_guba_all
{
  "template": "guba*",
  "order": 0,
  "settings": {
    "number_of_shards": 3
  },
  "mappings": {
    "post": {
      "properties": {
        "releaseTime": {
          "type": "date",
          "format": "yyyy-MM-dd HH:mm:ss"
        }
      }
    }
  }
}

GET _template/template_guba

GET guba/_search/
{
  "query": {
    "range": {
      "releaseTime": {
        "gte": "2014-10-13 10:14:00",
        "lte": "2014-10-13 11:14:00"
      }
    }
  },
  "aggs": {
    "stock_name": {
      "terms": {
        "field": "stock_id"
      },
      "aggs" : {
          "sentiment_stats" : {
            "terms" : { "field" : "sentiment" }
          }
      }
    }
  }
}
```
