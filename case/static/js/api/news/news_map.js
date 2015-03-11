var province_list = ["安徽", "北京", "重庆", "福建", "甘肃", "广东", "广西", "贵州", "海南", "河北", "黑龙江", "河南", "湖北", "湖南", "内蒙古", "江苏", "江西", "吉林", "辽宁", "宁夏", "青海", "山西", "山东", "上海", "四川", "天津", "西藏", "新疆", "云南", "浙江", "陕西", "台湾", "香港", "澳门"];
var topic = QUERY;
var START_TS = START_TS;
var END_TS = END_TS;
var DURING_INTERGER = POINT_INTERVAL;
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
function CaseMap(topic, start_ts, end_ts, pointInterval){
    this.query = topic;
    this.start_ts = start_ts;
    this.end_ts = end_ts;
    this.pointInterval = pointInterval;
    this.ts_list=[];
    this.dataMap = {};
    this.rank_city = [];
    this.mappoint_data;
    this.map_div_id_whole = 'map_div_whole';
    this.map_div_id_zone = 'map_div_zone';
    this.weibo_tab_id = 'Tableselect_2';
    this.weibo_cont_id = "weibo_ul_2";
    this.weibo_more_id = 'more_information_2';
    this.weibo_height_id = "content_control_height_2";

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

    this.whole_map_ajax_url = function(query, start_ts, end_ts, pointInterval, style, incremental){
        return "/evolution/topic_ajax_spatial_news/?start_ts=" + start_ts + "&end_ts=" + end_ts + '&pointInterval=' + pointInterval + '&topic=' + query + '&style=' + style + '&incremental=' + incremental
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
        '3': '总数'
    };
    // this.select_province_idx_list = [1, 5, 6, 14, 23, 30];
    this.myChart_whole;
    this.myChart_zone;
    this.disposeMyChartWhole = function () {
        if (this.myChart_whole) {
            this.myChart_whole.dispose();
            this.myChart_whole = false;
        }
    }
    this.disposeMyChartZone = function () {
        if (this.myChart_zone) {
            this.myChart_zone.dispose();
            this.myChart_zone = false;
        }
    }


    this.Index2Idx = {
        'origin': 1,
        'repost': 2,
        'global': 3
    }

    this.Index2Incre = {
        'growth': 0,
        'accumulative': 1
    }

    this.addSwitchMyChartListener = function(){
        var that = this;
        $('input:radio[name="optionsStatusWhole"]').on('change', function (e) {
            curIdxWhole = that.Index2Idx[e.target.value];
            that.showWholeMapChart();
        });
        $('input:radio[name="optionsStatusWholeSta"]').on('change', function (e) {
            incrementalWhole = that.Index2Incre[e.target.value];
            that.showWholeMapChart();
        });
        $('input:radio[name="optionsStatusZone"]').on('change', function (e) {
            curIdxZone = that.Index2Idx[e.target.value];
            that.showZoneChart();
        });
        $('input:radio[name="optionsStatusZoneSta"]').on('change', function (e) {
            incrementalZone = that.Index2Incre[e.target.value];
            that.showZoneChart();
        });
    }

    this.showWholeMapChart = function () {
        this.disposeMyChartWhole();
        this.initPullDrawMap();
    }
    this.showZoneChart = function (curSta) {
        this.disposeMyChartZone();
        this.initPullDrawZone();
    }


    this.addSwitchTabListener = function(){
        var that = this;
        var select_a;
        var unselect_a;
        $("#mapTabDiv").children("[status='wholemap']").click(function() {
            select_a = $(this);
            unselect_a = $(this).siblings('a');
            if(!select_a.hasClass('curr')) {
                select_a.addClass('curr');
                unselect_a.removeClass('curr');
                that.showWholeMapChart();
                that.showZoneChart();
            }
        });
    }
}

CaseMap.prototype.initPullDrawZone = function(sta){
    var ajax_url = this.whole_map_ajax_url(this.query, this.start_ts, this.end_ts, this.pointInterval, curIdxZone, incrementalZone);
    var myChart_zone = echarts.init(document.getElementById(this.map_div_id_zone));
    this.myChart_zone = myChart_zone;

    myChart_zone.showLoading({
        effect:'whirling'
    });

    var that = this;
    this.call_async_ajax_request(ajax_url, this.ajax_method, callback);

    function callback(data){
        myChart_zone.hideLoading();
        var province_data = data['province_data'];
        var ts_list = data['ts_list'];
        var date_list = [];
        for(var i=0; i<ts_list.length; i+= 1){
            date_list.push(new Date(parseInt(ts_list[i]) * 1000).format("yyyy年MM月dd日 hh:mm:ss"));
        }

        drawZoneChart(that, province_data, date_list, myChart_zone);

    }
}

CaseMap.prototype.initPullDrawMap = function(){
    var ajax_url = this.whole_map_ajax_url(this.query, this.start_ts, this.end_ts, this.pointInterval, curIdxWhole, incrementalWhole);
    var myChart_whole = echarts.init(document.getElementById(this.map_div_id_whole));
    this.myChart_whole = myChart_whole;

    myChart_whole.showLoading({
        effect:'whirling'
    });

    var that = this;
    this.call_async_ajax_request(ajax_url, this.ajax_method, callback);

    function callback(data){
        console.log(data);
        myChart_whole.hideLoading();
        var data_count = data["count"];
        var format_data = that.dataFormatter(data_count);
        var max_count = Math.ceil(data["max_count"] / 10) * 10;

        // show weibo
        var total_count = data["total_count"];
        that.rank_city = [];

        var length = Math.min(TOP_LIMIT, total_count.length);
        for(var j = 0; j < length; j++ ) {
            that.rank_city.push(total_count[j][0]);
        }
        drawWholeMap(that, format_data, max_count, myChart_whole);

        if (!top_city_news){
            top_city_news = data["top_city_news"];
        }
        drawtab(that.rank_city, that.weibo_tab_id, that.weibo_cont_id, that.weibo_more_id, that.weibo_height_id);
    }
}

// 默认加载总数,默认加载增量
var curIdxWhole = '3';
var curIdxZone = '3';
var incrementalWhole = '0';
var incrementalZone = '0';
var casemap = new CaseMap(topic, START_TS, END_TS, POINT_INTERVAL);
casemap.addSwitchTabListener();
casemap.addSwitchMyChartListener();

function drawZoneChart(that, data, ts_list, myChart_zone){
    var keyCity = that.pList;

    var option = {
        tooltip : {
            trigger: 'axis',
            orient: 'vertical',
            x: 'left',
            y: -20
        },
        
        legend: {
            data: keyCity,
            padding: 1,
            //orient: 'vertical',
            y: 'top',
            x: 'right'
        },
        
        toolbox: {
            show : true,
            orient : 'vertical',
            x:'right',
            y:'center',
            feature : {
                mark : {show: true},
                dataView : {show: true,
                    readOnly: false,
                    optionToContent:function (v){
                        var results = '';
                        for (var t = 0;t < v.xAxis[0]['data'].length;t++){
                            var sdata2str = v.xAxis[0]['data'][t];
                            sdata2str += ':\n';
                            for (var i = 1;i < v.series.length;i++){
                                var sname = v.series[i]['name'];
                                var sdata = v.series[i]['data'];
                                sdata2str += sname + ':' + sdata[i] + ',';
                            }
                            sdata2str += '\n';
                            results += sdata2str;
                        }
                        return results;
                    }
                },
                // magicType : {show: true, type: ['line', 'bar', 'stack', 'tiled']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        calculable : true,
        xAxis : [{
            type : 'category',
            boundaryGap : false,
            data : ts_list,
            axisLabel: {
                /*
                formatter: function(s){
                    return new Date(parseInt(s) * 1000).format("yyyy年MM月dd日 hh:mm:ss");
                }*/
            }
        }],
            
        yAxis : [{
            type : 'value'
        }],
        series : []
    };
    var selected = {};
    var series = [];

    var singleData;
    var city;
    var seriesData;
    for (var i = 0, l = keyCity.length; i < l; i++) {
        city = keyCity[i];
        
        seriesData = data[city];
        series.push({
            name: city,
            type: 'line',
            stack: '总量',
            data: seriesData
        });
        selected[city] = false;
    }
    var markNum = 3; // number of true legends
    for(var i=0;i < markNum;i++){
        selected[that.rank_city[i]] = true;
    }
    option.legend.selected = selected;
    option.series = series;

    myChart_zone.setOption(option);
}

function drawWholeMap(that, fdata, max_count, myChart_whole){
    var get_bar_series_data_ele = function(data) {
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
                            color : 'rgb(240,22,77)',
                            fontWeight : 'bold'
                        }
                    }
                }
            },
            data: data
        }
    }
    var get_map_series_data_ele = function(markPointData, data) {
        return {
            name:'微博数量',
            type: 'map',
            mapType: 'china',
            roam: false,
            itemStyle:{
                normal:{label:{show:true}},
                emphasis:{label:{show:true}}
            },
            mapLocation: {
                x: 350,
                y: 80
            },
            data: data,
            markPoint:{
                symbolSize: function(v){
                    return 15;
                },
                itemStyle : {
                    normal:{
                        color:'rgb(240,22,77)'
                    },
                    emphasis:{
                        label:{
                            show:false
                        }
                    }
                },
                data : markPointData
            },
            geoCoord : city2lnglat
        }
    }

    var option_data_arr = [];
    var date_list = [];
    for(var timestamp in fdata){
        var date = new Date(timestamp * 1000).format("yyyy年MM月dd日 hh:mm:ss");
        date_list.push(date);

        var markPointData = [];
        var markNum = 5; // number of markpoints
        for(var i=0;i < markNum;i++){
            for (var m=0;m < that.pList.length;m++){
                if (that.pList[m] == that.rank_city[i]){
                    markPointData.push(fdata[timestamp][m]);
                    break;
                }
            }
        }

        var darr = fdata[timestamp];
        darr.sort(function(a, b) {
            return a.value - b.value
        });

        var sorted_plist = [];
        for(var i in darr){
            sorted_plist.push(darr[i]['name']);
        }

        var map_series_data = get_map_series_data_ele(markPointData, darr);
        var bar_series_data = get_bar_series_data_ele(darr);
        var option_data = {
            title : {
                x: 'center',
                textStyle:{
                    fontSize: 12,
                }
            },

            tooltip:{
                trigger: 'item'
            },

            toolbox:{
                show: true,
                orient: 'vertical',
                x: 'right',
                y: 'top',
                feature:{
                    mark:{show:true},
                    dataView:{show:true,
                        readOnly:false,
                        optionToContent:function(v){
                            var results = '';
                            for (var i=1;i < v.series.length;i++){
                                // var sname = v.series[i]['name'];
                                var sdata = v.series[i]['data'];
                                var sdata2str = '';
                                for (var m = 0;m < sdata.length;m++){
                                    sdata2str += sdata[m]['name'] + ':' + sdata[m]['value'] + ';';
                                }
                                results += sdata2str;
                            }
                            return results;
                        }
                    },
                    restore:{show:true},
                    saveAsImage:{show:true}
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
                padding: 10,
                textStyle: {
                    color: 'orange'
                }
            },

            grid:{
                x: 50,
                x2: 80,
                y2: 10,
                borderWidth:0
            },
            xAxis : [
                {
                    type : 'value',
                    position: 'bottom',
                    splitLine: {show: true},
                    boundaryGap : [0, 0.01],
                    axisLabel:{
                        show:true,
                        formatter:'{value}'
                    },
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
            x: 20,
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
    myChart_whole.setOption(option);
}

