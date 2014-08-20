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

    this.pList = ['安徽', '北京', '重庆', '福建', '甘肃', '广东','广西','贵州','海南','河北','黑龙江','河南','湖北','湖南','内蒙古','江苏','江西','吉林','辽宁','宁夏','青海','山西','山东','上海','四川','天津','西藏','新疆','云南','浙江','陕西','台湾','香港','澳门'];
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
    }
}

// instance method, 取各地区时间序列数据, 并绘图
CaseMap.prototype.initPullDrawMap = function(){
    //for(var sta in this.status){
        var sta = '4';
        var ajax_url = this.whole_map_ajax_url(this.query, this.start_ts, this.end_ts, this.pointInterval, sta);
        //var myChart = echarts.init(document.getElementById(this.map_div_id));
        //myChart.showLoading({
        //    text: '努力加载数据中...'
        //});
        var that = this;
        this.call_async_ajax_request(ajax_url, this.ajax_method, callback);
    //}

    function callback(data){
        myChart.hideLoading();
        var data_count = data["count"];
        var max_count = data["max_count"];
        var format_data = that.dataFormatter(data_count);
        drawWholeMap(that, format_data, max_count, myChart);
    }
}

require(
    [
        '/static/js/echarts-2.0.1/src/echarts',
        //'/static/js/echarts-2.0.1/src/chart/line',
        //'/static/js/echarts-2.0.1/src/chart/bar',
        //'/static/js/echarts-2.0.1/src/chart/scatter',
        //'/static/js/echarts-2.0.1/src/chart/radar',
        //'/static/js/echarts-2.0.1/src/chart/map'
    ],
    function (ec) {
        EC_READY = true;
        //myChart0 = ec.init(document.getElementById('g0')).showLoading({effect:'bubble'});
        myChart1 = ec.init(document.getElementById('map_div')).showLoading({effect:'bubble'});
        //myChart20 = ec.init(document.getElementById('g20')).showLoading({effect:'bubble'});
        //myChart21 = ec.init(document.getElementById('g21')).showLoading({effect:'bubble'});
        //myChart22 = ec.init(document.getElementById('g22')).showLoading({effect:'bubble'});
        //myChart3 = ec.init(document.getElementById('g3')).showLoading({effect:'bubble'});

        /*
        require(
            ['air'],
            function (airData) {
                DATA_READY = true;
                airData = testData;
                console.log(airData);
                //$('#time')[0].innerHTML = airData[0].time_point.replace(/[T|Z]/g, ' ')
                var ecConfig = require('echarts/config');
                //console.log(airData);
                //data.format(airData,testData);
                //showTabContent(0, oCurTabIdx);
                //showTabContent(1);
                //showTabContent(2);
                //showTabContent(3, rCurTabIdx);
                //myChart0.on(ecConfig.EVENT.MAP_ROAM, extMark);
                myChart1.on(ecConfig.EVENT.LEGEND_SELECTED, legendShare);
                //myChart1.on(ecConfig.EVENT.RESTORE, legendShare);
            }
         );*/
    }
);

function legendShare(){
}

var casemap = new CaseMap(START_TS, END_TS, DURING_INTERGER);
casemap.initPullDrawMap();


function drawWholeMap(that, fdata, max_count, myChart){
    var get_series_data_ele = function(name, markPointData, data, geoCoord) {
        return [{
            'name': name,
            'type': 'map',
            mapType: 'china',
            roam: true,
            itemStyle:{
                normal:{label:{show:true}},
                emphasis:{label:{show:true}}
            },
            'data': data,
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
        }]
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
        var series_data = get_series_data_ele(name, markPointData, fdata[timestamp], geoCoord);
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
                text:['高', '低'], // 文本，默认为数值文本
                calculable: true,
                x: 'left',
                padding:2,
                color: ['orangered', 'yellow', 'lightskyblue']
            },

            series : series_data
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
            autoPlay: false,
            x: 30,
            y: 20,
            playInterval: 1000,
            type: 'number',
        },
        legend: {
            data: that.pList
        },
        options: option_data_arr
    };

    myChart.setOption(option);
}

