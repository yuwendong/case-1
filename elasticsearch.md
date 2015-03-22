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
