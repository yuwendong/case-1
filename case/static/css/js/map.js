
     //var pList = ['安徽','北京','重庆','福建','甘肃','广东','广西','贵州','海南','河北','黑龙江','河南','湖北','湖南','内蒙古','江苏','江西'，'吉林','辽宁','宁夏','青海','山西','山东','上海','四川','天津','西藏','新疆','云南','天津','浙江','陕西','台湾','香港','澳门'];


    $(document).ready(function(){   //网页加载时执行下面函数
      drawmap();
    })
    var map_data = {};
    var time_t=[];
    var time_af=[];
    var ots = 1377966600;

    function drawmap(){

            map(ots);

            time_t=get_time();

            for (var i = 0; i < time_t.length; i++){

                ns= new Date(parseInt(time_t[i]) * 1000).toLocaleString();

                time_af.push(ns);
            }
            console.log(dataMap.dataweibo[time_t[0]][1]);
           //console.log(time_af);
           // var unixTimestamp = new Data(Unix 1377968400*1000);
           //  var commonTime=unixTimestamp.toLocaleString();
           //  console.log(commonTime);

            //console.log(dataMap.dataweibo);
            

            //console.log(ts_list);
    var option = {
        timeline:{
            data:time_af,
            label : {
                show:true,
                interval: 0,
                //rotate:30,
                formatter : function(s) {
                    return s.slice(10, 16);
                }
            },
            autoPlay : true,
            x:30,
            y:20,
            playInterval : 1000,
            type: 'number',
        },
        options:[
            {
                title : {
                  
                    x: 'center',
                textStyle:{
                    fontSize: 12,
                    }                    
                },
                tooltip : {'trigger':'item'},
                toolbox : {
                    'show':true, 
                    'feature':{
                        'mark':{'show':true},
                        'dataView':{'show':true,'readOnly':false},
                        'restore':{'show':true},
                        'saveAsImage':{'show':true}
                    }
                },
                dataRange: {
                    min: 0,
                    max : 53000,
                    text:['高','低'],           // 文本，默认为数值文本
                    calculable : true,
                    x: 'left',
                    padding:2,
                    color: ['orangered','yellow','lightskyblue']
                },
                series : [
                    {
                        'name':'微博数量',
                        'type':'map',
                        mapType: 'china',
                        roam: true,
                        itemStyle:{
                            normal:{label:{show:true}},
                            emphasis:{label:{show:true}}
                        },
                        'data': dataMap.dataweibo[time_t[0]],
                        markPoint:{
                            symbolSize: 20,//用于修改标记label的大小
                            itemStyle : {
                                normal:{
                                    color:'red'//用于修改标记label的颜色
                                },
                                emphasis:{label:{show:true}}
                            },
                            data : [
                            dataMap.dataweibo[time_t[0]][1],//北京的数据
                            dataMap.dataweibo[time_t[0]][23],//上海的数据
                            dataMap.dataweibo[time_t[0]][5],//广东的数据
                            dataMap.dataweibo[time_t[0]][26],//西藏的数据
                            dataMap.dataweibo[time_t[0]][27],//新疆的数据
                            {name:"海外" ,value: 250}

                            ]
                        },
                        geoCoord : {
                        "北京":[116.46,39.92], // 支持数组[经度，维度]
                        "上海":[121.48,31.22], 
                        "广东":[113.23,23.16],
                        "西藏":[91.11,29.97],
                        "新疆":[87.68,43.77], 
                        "海外":[126.9,37.51]
                        }
                    }
                ]
            },
            {
                title : {
                    x: 'center'},
                series : [
                    {
                        'name':'微博数量',
                        'type':'map',
                        mapType: 'china',
                        roam: true,
                        itemStyle:{
                            normal:{label:{show:true}},
                            emphasis:{label:{show:true}}
                        },
                        'data': dataMap.dataweibo['1377970200'],
                        markPoint:{
                            symbolSize: 20,//用于修改标记label的大小
                            itemStyle : {
                                normal:{
                                    color:'red'//用于修改标记label的颜色
                                },
                                emphasis:{label:{show:true}}
                            },
                            data : [
                            dataMap.dataweibo[time_t[1]][1],//北京的数据
                            dataMap.dataweibo[time_t[1]][23],//上海的数据
                            dataMap.dataweibo[time_t[1]][5],//广东的数据
                            dataMap.dataweibo[time_t[1]][26],//西藏的数据
                            dataMap.dataweibo[time_t[1]][27],//新疆的数据
                            {name:"海外" ,value: 100}
                            ]
                        },
                        geoCoord : {
                        "北京":[116.46,39.92], // 支持数组[经度，维度]
                        "上海":[121.48,31.22], 
                        "广东":[113.23,23.16],
                        "西藏":[91.11,29.97],
                        "新疆":[87.68,43.77],
                        "海外":[126.9,37.51]
                        }//若要增加其他的城市，现在data中找到相应的城市数据，再在geoCoord中加入相应的经纬度即可
                    }
                ]
            },
            {
                title : {
                    x: 'center'},
                series : [
                    {
                        'name':'微博数量',
                        'type':'map',
                        mapType: 'china',
                        roam: true,
                        itemStyle:{
                            normal:{label:{show:true}},
                            emphasis:{label:{show:true}}
                        },
                        'data': dataMap.dataweibo['1377972000'],
                        markPoint:{
                            symbolSize: 20,//用于修改标记label的大小
                            itemStyle : {
                                normal:{
                                    color:'red'//用于修改标记label的颜色
                                },
                                emphasis:{label:{show:true}}
                            },
                            data : [
                            dataMap.dataweibo[time_t[2]][1],//北京的数据
                            dataMap.dataweibo[time_t[2]][23],//上海的数据
                            dataMap.dataweibo[time_t[2]][5],//广东的数据
                            dataMap.dataweibo[time_t[2]][26],//西藏的数据
                            dataMap.dataweibo[time_t[2]][27],
                            {name:"海外" ,value: 400}//新疆的数据
                            ]
                        },
                        geoCoord : {
                        "北京":[116.46,39.92], // 支持数组[经度，维度]
                        "上海":[121.48,31.22], 
                        "广东":[113.23,23.16],
                        "西藏":[91.11,29.97],
                        "新疆":[87.68,43.77],
                        "海外":[126.9,37.51]
                        }
                    }
                ]
            },
            //只改了前三个时间序列的数值，后面的series修改同上，只要把对应日期修改即可
            {          
                title : {
                    x: 'center'},
                series : [
                    {
                        'name':'微博数量',
                        'type':'map',
                        mapType: 'china',
                        roam: true,
                        itemStyle:{
                            normal:{label:{show:true}},
                            emphasis:{label:{show:true}}
                        },
                        'data': dataMap.dataweibo[time_t[3]],
                        markPoint:{
                            symbolSize: 20,//用于修改标记label的大小
                            itemStyle : {
                                normal:{
                                    color:'red'//用于修改标记label的颜色
                                },
                                emphasis:{label:{show:true}}
                            },
                            data : [
                            dataMap.dataweibo[time_t[3]][1],//北京的数据
                            dataMap.dataweibo[time_t[3]][23],//上海的数据
                            dataMap.dataweibo[time_t[3]][5],//广东的数据
                            dataMap.dataweibo[time_t[3]][26],//西藏的数据
                            dataMap.dataweibo[time_t[3]][27],
                            {name:"海外" ,value: 600}//新疆的数据
                            ]
                        },
                        geoCoord : {
                        "北京":[116.46,39.92], // 支持数组[经度，维度]
                        "上海":[121.48,31.22], 
                        "广东":[113.23,23.16],
                        "西藏":[91.11,29.97],
                        "新疆":[87.68,43.77],
                        "海外":[126.9,37.51]
                        }
                    }
                ]
            }
        ]
    };
    var myChart = echarts.init(document.getElementById('map_div'));
    myChart.setOption(option); 

 }
