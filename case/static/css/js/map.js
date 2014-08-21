var START_TS = 1377964800;
var END_TS = 1378051200;
var DURING_INTERGER = 60 * 60;

// Date format
Date.prototype.format = function(format) { 
    var o = { 
    "M+" : this.getMonth()+1, //month 
    "d+" : this.getDate(),    //day 
    "h+" : this.getHours(),   //hour 
    "m+" : this.getMinutes(), //minute 
    "s+" : this.getSeconds(), //second 
    "q+" : Math.floor((this.getMonth()+3)/3),  //quarter 
    "S" : this.getMilliseconds() //millisecond 
    } 
    if(/(y+)/.test(format)) 
    format=format.replace(RegExp.$1, (this.getFullYear()+"").substr(4 - RegExp.$1.length)); 
    for(var k in o)
    if(new RegExp("("+ k +")").test(format)) 
        format = format.replace(RegExp.$1, RegExp.$1.length==1 ? o[k] : ("00"+ o[k]).substr((""+ o[k]).length)); 
    return format; 
}

// map类
function CaseMap(start_ts, end_ts, pointInterval){
    this.query = '中国';
    this.start_ts = start_ts;
    this.end_ts = end_ts;
    this.pointInterval = pointInterval;
    this.during = end_ts - start_ts;
    this.ts_list=[];
    this.dataMap = {};
    this.mappoint_data;
    this.map_div_id = 'map_div';

    this.pList = ['安徽', '北京', '重庆', '福建', '甘肃', '广东','广西','贵州','海南','河北','黑龙江','河南','湖北','湖南','内蒙古','江苏','江西','吉林','辽宁','宁夏','青海','山西','山东','上海','四川','天津','西藏','新疆','云南','浙江','陕西','台湾','香港','澳门', '海外'];
    this.dataFormatter = function(obj){
        var temp;
        for (var year in obj) {
            temp = obj[year];
            for (var i = 0, l = temp.length; i < l; i++) {
                obj[year][i] = {
                    name : this.pList[i],
                    value : temp[i]
                }
            }
        }
        return obj;
    }

    this.whole_map_ajax_url = function(query, start_ts, end_ts, during, style){
        return "/evolution/topic_ajax_spatial/?start_ts=" + start_ts + "&end_ts=" + end_ts + '&topic=' + query + '&style=' + style
    }
    this.ajax_method = "GET";
    this.call_sync_ajax_request = function(url, method, callback){
        $.ajax({
            url: url,
            type: method,
            dataType: "json",
            async: false,
            success: callback
        })
    }
    this.call_async_ajax_request = function(url, method, callback){
        $.ajax({
            url: url,
            type: method,
            dataType: "json",
            async: true,
            success: callback
        })
    }
    this.status = {
        '1': '原创',
        '2': '转发',
        '3': '评论',
        '4': '总数'
    };
    this.select_province_idx_list = [1, 5, 23];
    this.geoCoordObj = {
        "北京":[116.46,39.92], // 支持数组[经度，维度]
        "上海":[121.48,31.22],
        "广东":[113.23,23.16],
        "西藏":[91.11,29.97],
        "新疆":[87.68,43.77],
        "海外":[126.9,37.51]
    };

    this.myChart;
    this.disposeMyChart = function () {
        if (this.myChart) {
            this.myChart.dispose();
            this.myChart = false;
        }
    }

    this.Index2Idx = {
        'origin': 1,
        'repost': 2,
        'comment': 3,
        'global': 4
    }

    this.addSwitchMyChartListener = function(){
        var that = this;
        $('input:radio[name="optionsStatus"]').on('change', function (e) {
            var curIndex = e.target.value;
            var curIdx = that.Index2Idx[curIndex];
            that.showMyChart(curIdx);
        });
    }

    this.showMyChart = function (curSta) {
        this.disposeMyChart();
        this.initPullDrawMap(curSta);
    }
}

// instance method, 取各地区时间序列数据, 并绘图
CaseMap.prototype.initPullDrawMap = function(sta){
    var ajax_url = this.whole_map_ajax_url(this.query, this.start_ts, this.end_ts, this.pointInterval, sta);
    var myChart = echarts.init(document.getElementById(this.map_div_id));
    this.myChart = myChart;

    myChart.showLoading({
        text: '努力加载数据中...'
    });
    var that = this;
    this.call_async_ajax_request(ajax_url, this.ajax_method, callback);

    function callback(data){
        myChart.hideLoading();
        var data_count = data["count"];
        var max_count = data["max_count"];
        var format_data = that.dataFormatter(data_count);
        drawWholeMap(that, format_data, max_count, myChart);
    }
}

// 默认加载总数
var curIdx = '1';
var casemap = new CaseMap(START_TS, END_TS, DURING_INTERGER);
casemap.showMyChart(curIdx);
casemap.addSwitchMyChartListener();


function drawWholeMap(that, fdata, max_count, myChart){
    var get_bar_series_data_ele = function(name, data) {
        return {
            type: 'bar',
            itemStyle : {
                normal : {
                    /*
                    color : (function (){
                        var zrColor = require('zrender/tool/color');
                        return zrColor.getLinearGradient(
                            0, 80, 0, 500,
                            [[0, 'red'],[0.2, 'orange'],[1, 'yellow']]
                        )
                    })(),*/
                    label : {
                        show : false
                    }
                },
                emphasis : {
                    label : {
                        show : true,
                        textStyle : {
                            color : 'orange',
                            fontWeight : 'bold'
                        }
                    }
                }
            },
            'data': data
        }
    }
    var get_map_series_data_ele = function(name, markPointData, data, geoCoord) {
        return {
            name: name,
            type: 'map',
            mapType: 'china',
            roam: true,
            itemStyle:{
                normal:{label:{show:true}},
                emphasis:{label:{show:true}}
            },
            mapLocation: {
                x: 'right',
                y: 80
            },
            data: data,
            markPoint:{
                symbolSize: 20, // 用于修改标记label的大小
                itemStyle : {
                    normal:{
                        color:'green' // 用于修改标记label的颜色
                    },
                    emphasis:{label:{show:true}}
                },
                data : markPointData
            },
            geoCoord : geoCoord
        }
    }

    var option_data_arr = [];
    var ts_list = [];
    var date_list = [];
    for(var timestamp in fdata){
        var date = new Date(timestamp * 1000).format("yyyy年MM月dd日 hh:mm:ss");
        ts_list.push(timestamp);
        date_list.push(date);

        var markPointData = [];
        var geoCoord = {};
        for(var i in that.select_province_idx_list){
            var idx = that.select_province_idx_list[i];
            markPointData.push(fdata[timestamp][idx]);
            geoCoord[that.pList[idx]] = that.geoCoordObj[that.pList[idx]];
        }

        //markPointData.push({name:"海外" ,value: 250});
        var name = '微博数量';
        var darr = fdata[timestamp];
        darr.sort(function(a, b) {
            return a.value - b.value
        });
        var sorted_plist = [];
        for(var i in darr){
            sorted_plist.push(darr[i]['name']);
        }

        var map_series_data = get_map_series_data_ele(name, markPointData, darr, geoCoord);
        var bar_series_data = get_bar_series_data_ele(name, darr);
        var option_data = {
            title : {
                x: 'center',
                textStyle:{
                    fontSize: 12,
                }
            },

            tooltip:{
                'trigger': 'item'
            },

            toolbox:{
                'show': true,
                'feature':{
                    'mark':{'show':true},
                    'dataView':{'show':true,'readOnly':false},
                    'restore':{'show':true},
                    'saveAsImage':{'show':true}
                }
            },

            dataRange: {
                min: 0,
                max : max_count,
                orient: 'vertical',
                color: ['orangered', 'yellow', 'lightskyblue'],
                //color:['red','yellow'],
                //color: ['orangered', 'yellow', 'lightskyblue']
                text:['高', '低'], // 文本，默认为数值文本
                calculable: true,
                x: 'right',
                y: 'bottom',
                padding:10,
                textStyle: {
                    color: 'orange'
                }
            },

            grid:{
                x: 50,
                x2: 200,
                y2: 10,
                borderWidth:0
            },
            xAxis : [
                {
                    type : 'value',
                    position: 'bottom',
                    name: '（条）',
                    splitLine: {show: false},
                    boundaryGap : [0, 0.01]
                }
            ],
            yAxis : [
                {
                    type : 'category',
                    position: 'left',
                    splitLine: {show:false},
                    axisLabel: {
                        interval:0
                    },
                    data: sorted_plist
                }
            ],
            series : [map_series_data, bar_series_data]
        };
        option_data_arr.push(option_data);
    }

    var option = {
        timeline:{
            data: date_list,
            label: {
                show:true,
                interval: 'auto',
                //rotate:30,
                formatter : function(s) {
                    return s.slice(12, 17);
                }
            },
            autoPlay: true,
            x: 30,
            y: 20,
            playInterval: 1000,
            type: 'number',
        },
        legend: {
            show: true,
            data: that.pList
        },
        options: option_data_arr
    };

    myChart.setOption(option);
}

/*
myChart = echarts.init(document.getElementById('spatial_trend_div'));
myChart.setOption(option1());

function option1 (name) {
    var keyCity = [
        '北京','上海','广州','长春','长沙','成都','福州','哈尔滨','沈阳','杭州','呼和浩特',
        '昆明','南京','贵阳','太原','天津','武汉','西安','郑州','重庆','济南',
        '银川','石家庄','乌鲁木齐','南昌','海口','兰州','西宁','合肥','南宁','深圳',
        '包头','大连','大同','保定','东莞','佛山','桂林','开封','连云港',
        '廊坊','宁波','齐齐哈尔','泉州','绍兴','苏州','唐山','无锡','延安',
        '扬州','徐州','烟台','宜宾','玉溪','湛江','中山','珠海','淄博',
        '威海','潍坊','温州','汕头','青岛','厦门','九江','秦皇岛','洛阳',
        '北京','上海','广州','重庆','天津','太原','沈阳','大连','长春',
        '南京','杭州','宁波','合肥','福州','厦门','南昌','济南','青岛',
        '郑州','武汉','长沙','深圳','南宁','海口','成都','贵阳','昆明',
        '拉萨','西安','兰州','西宁','银川','哈尔滨','石家庄','呼和浩特','乌鲁木齐'
    ];
    var option = {
        title : {
            text: '重点城市对比',
            subtext: 'data from PM25.in',
            sublink: 'http://www.pm25.in',
            x:'right',
            y:'bottom'
        },
        tooltip : {
            trigger: 'axis',
            formatter: function (v) {
                var res = v[0][1] + '<br/>';
                if (v.length < 5) {
                    for (var i = 0, l = v.length; i < l; i++) {
                        res += v[i][0] + ' : ' + v[i][2] + '<br/>';
                    }
                }
                else {
                    for (var i = 0, l = v.length; i < l; i++) {
                        res += v[i][0] + ' : ' + v[i][2] + ((i + 1) % 3 == 0 ? '<br/>' : ' ');
                    }
                }
                return res;
            }
        },
        legend: {
            data: keyCity
        },
        toolbox: {
            show : true,
            orient : 'vertical',
            x: 'right',
            y: 'center',
            feature : {
                mark : {show: true},
                dataView : {show: true, readOnly: false},
                magicType : {show: true, type: ['line', 'bar']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        grid:{
            x: 50,
            y: 80,
            x2: '32%',
            borderWidth:0
        },
        xAxis : [
            {
                type : 'category',
                splitLine : {show : false},
                data : ['AQI','PM2.5','PM10','NO2','O3','SO2']
            }
        ],
        yAxis : [
            {
                type : 'value',
                splitArea : {show : true},
                splitLine : {show : true}
            }
        ],
        polar : [
           {
               indicator : [
                   { text: 'AQI'},
                   { text: 'PM2.5'},
                   { text: 'PM10'},
                   { text: 'NO2'},
                   { text: 'O3'},
                   { text: 'SO2'}
                ],
                center : ['84%', 230],
                radius : 120
            }
        ]
    };
    
    var selected = {};
    var series = [
        {
            name: '对比',
            type: 'radar',
            tooltip: {
                trigger:'axis',
                formatter: function (v) {
                    var res = v[0][3] + '<br/>';
                    if (v.length < 5) {
                        for (var i = 0, l = v.length; i < l; i++) {
                            res += v[i][1] + ' : ' + v[i][2] + '<br/>';
                        }
                    }
                    else {
                        for (var i = 0, l = v.length; i < l; i++) {
                            res += v[i][1] + ' : ' + v[i][2] + ((i + 1) % 3 == 0 ? '<br/>' : ' ');
                        }
                    }
                    return res;
                }
            },
            itemStyle: {
                normal: {
                    lineStyle: {
                        width: 1
                    }
                }
            },
            data: []
        }
    ];
    var cityToData = data.cityToData;
    var singleData;
    var city;
    var seriesData;
    for (var i = 0, l = keyCity.length; i < l; i++) {
        city = keyCity[i];
        singleData = cityToData[city];
        if (typeof singleData == 'undefined') {
            continue;
        }
        seriesData = [
            singleData.aqi, 
            singleData.pm2_5, 
            singleData.pm10, 
            singleData.no2, 
            singleData.o3, 
            singleData.so2
        ];
        series[0].data.push({
            name: city,
            value: seriesData
        });
        series.push({
            name: city,
            type: 'bar',
            barGap:'5%',
            barCategoryGap:'10%',
            data: seriesData
        });
        selected[city] = false;
    }
    selected['北京'] = true;
    selected['上海'] = true;
    selected['广州'] = true;
    //selected['重庆'] = true;
    //selected['哈尔滨'] = true;
    //selected['乌鲁木齐'] = true;
    //selected['拉萨'] = true;
    option.legend.selected = selected;
    //option.series = series;
    //console.log(option);
    return option;
}*/

