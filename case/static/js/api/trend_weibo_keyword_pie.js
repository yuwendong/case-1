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

// TrendsLine Constructor
function TrendsLine(query, start_ts, end_ts, pointInterval){
    //instance property
    this.query = query;
    this.start_ts = start_ts; // 开始时间戳
    this.end_ts = end_ts; // 终止时间戳
    this.pointInterval = pointInterval; // 图上一点的时间间隔
    this.during = end_ts - start_ts; // 整个时间范围
    this.pie_ajax_url = function(query, end_ts, during){
        return "/moodlens/pie/?ts=" + end_ts + "&query=" + query + "&during=" + during;
    }
    this.keywords_ajax_url = function(query, end_ts, during, emotion){
        return "/moodlens/keywords_data/?ts=" + end_ts + "&query=" + query + "&during=" + during + "&emotion=" + emotion;
    }
    this.weibos_ajax_url = function(query, end_ts, during, emotion, limit){
        return "/moodlens/weibos_data/?query=" + query + "&ts=" + end_ts + "&during=" + during + "&limit=" + limit + "&emotion=" + emotion;
    }
    this.count_ajax_url = function(query, end_ts, during, emotion){
        return "/moodlens/data/?query=" + query + "&ts=" + end_ts + "&during=" + during + "&emotion=" + emotion;
    }
    this.peak_ajax_url = function(data, ts_list, during, emotion){
        return "/moodlens/emotionpeak/?lis=" + data.join(',') + "&ts=" + ts_list + '&during=' + during + "&emotion=" + emotion;
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
    this.range_count_data = {};
    this.range_keywords_data = {};
    this.range_weibos_data = {};
    this.top_keywords_limit = 50; // 和计算相关的50，实际返回10
    this.top_weibos_limit = 50; // 和计算相关的50，实际返回10
    this.max_keywords_size = 50;
    this.min_keywords_size = 2;
    this.pie_title = '情绪饼图';
    this.pie_series_title = '情绪占比';
    this.pie_div_id = 'pie_div';
    this.trend_div_id = 'trend_div';
    this.trend_title = '情绪走势图';
    this.trend_chart;

    this.names = {
        'happy': '高兴',
        'angry': '愤怒',
        'sad': '悲伤'
    }

    this.trend_count_obj = {
        'ts': [], // 时间数组
        'count': {},
        'ratio': {}
    };

    for (var name in this.names){
        this.trend_count_obj['count'][name] = [];
        this.trend_count_obj['ratio'][name] = [];
    }
}

// instance method, 初始化时获取整个时间段的饼图数据并绘制
TrendsLine.prototype.initPullDrawPie = function(){
    that = this;
    var names = this.names;
    var ajax_url = this.pie_ajax_url(this.query, this.end_ts, this.during);
    this.call_async_ajax_request(ajax_url, this.ajax_method, range_count_callback);

    function range_count_callback(data){
        var pie_data = [];
        for (var status in data){
            var count = data[status];
            pie_data.push({
                value: count,
                name: names[status]
            })
        }

        var pie_title = that.pie_title;

        var pie_series_title = that.pie_series_title;

        var legend_data = [];
        for (var name in names){
            legend_data.push(names[name]);
        }

        var pie_div_id = that.pie_div_id;

        refreshDrawPie(pie_data, pie_title, pie_series_title, legend_data, pie_div_id);
    }
}

// 绘制饼图方法
function refreshDrawPie(pie_data, pie_title, pie_series_title, legend_data, pie_div_id) {
    var option = {
        backgroundColor: '#FFF',
        color: ['#11c897', '#fa7256', '#6e87d7'],
        title : {
            text: '', // pie_title,
            x: 'center',
            textStyle:{
                fontWeight: 'lighter',
                fontSize: 13
            }
        },
        toolbox: {
            show: true,
            feature : {
                mark : {show: true},
                dataView : {show: true, readOnly: false},
                //magicType : {show: true, type: ['line', 'bar']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        tooltip: {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)",
            textStyle: {
                fontWeight: 'bold',
                fontFamily: 'Microsoft YaHei'
            }
        },
        legend: {
            orient:'vertical',
            x : 'left',
            data: legend_data,
            textStyle: {
                fontWeight: 'bold',
                fontFamily: 'Microsoft YaHei'
            }
        },

        calculable : true,
        series : [
            {
                name: pie_series_title,
                type: 'pie',
                radius : '50%',
                center: ['50%', '60%'],
                itemStyle: {
                    normal: {
                        label: {
                            position: 'inner',
                            formatter: "{d}%",
                            textStyle: {
                                fontWeight: 'bold',
                                fontFamily: 'Microsoft YaHei'
                            }
                        },
                        labelLine: {
                            show: false
                        }
                    },
                    emphasis: {
                        label: {
                            show: true,
                            formatter: "{b}\n{d}%",
                            textStyle: {
                                fontWeight: 'bold',
                                fontFamily: 'Microsoft YaHei'
                            }
                        }
                    }
                },
                data: pie_data
            }
        ],
        textStyle: {
            fontWeight: 'bold',
            fontFamily: 'Microsoft YaHei'
        }
    };

    var myChart = echarts.init(document.getElementById(pie_div_id));
    myChart.setOption(option);
}

// instance method, 初始化时获取整个时间范围的关键词云数据并绘制
TrendsLine.prototype.initPullDrawKeywords = function(){
    that = this;

    var names = this.names;

    var min_keywords_size = this.min_keywords_size;
    var max_keywords_size = this.max_keywords_size;

    var emotion = 'global';

    var ajax_url = this.keywords_ajax_url(this.query, this.end_ts, this.during, emotion);
    this.call_async_ajax_request(ajax_url, this.ajax_method, range_keywords_callback);

    function range_keywords_callback(data){
        refreshDrawKeywords(min_keywords_size, max_keywords_size, data, emotion);
    }
}

// 根据权重决定字体大小
function defscale(count, mincount, maxcount, minsize, maxsize){
    if(maxcount == mincount){
        return (maxsize + minsize) * 1.0 / 2
    }else{
        return minsize + 1.0 * (maxsize - minsize) * Math.pow((count / (maxcount - mincount)), 2)
    }
}

// 画关键词云图
function refreshDrawKeywords(min_keywords_size, max_keywords_size, keywords_data, emotion){
    $("#keywords_cloud_div").empty();
    if (keywords_data == {}){
        $("#keywords_cloud_div").append("<a style='font-size:1ex'>关键词云数据为空</a>");
    }
    else{
        var min_count, max_count = 0, words_count_obj = {};
        for (var keyword in keywords_data){
            var count = keywords_data[keyword];
            if(count > max_count){
                max_count = count;
            }
            if(!min_count){
                min_count = count;
            }
            if(count < min_count){
                min_count = count;
            }
            words_count_obj[keyword] = count;
        }

        var colors = {
            'global': '#666',
            'happy': '#11c897',
            'angry': '#fa7256',
            'sad': '#6e87d7'
        }
        var color = colors[emotion];

        for(var keyword in words_count_obj){
            var count = words_count_obj[keyword];
            var size = defscale(count, min_count, max_count, min_keywords_size, max_keywords_size);
            $('#keywords_cloud_div').append('<a><font style="color:' + color +  '; font-size:' + size + 'px;">' + keyword + '</font></a>');
        }

        on_load();
    }
}

// instance method, 初始化时获取关键微博数据
TrendsLine.prototype.initPullWeibos = function(){
    var names = this.names;

    var weibos_data = [];
    that = this;
    for (var name in names){
        var ajax_url = this.weibos_ajax_url(this.query, this.end_ts, this.during, name, this.top_weibos_limit);
        this.call_sync_ajax_request(ajax_url, this.ajax_method, range_weibos_callback);
    }

    function range_weibos_callback(data){
        for(var name in names){
            if(name in data){
                var weibos_list = data[name];
                that.range_weibos_data[name] = weibos_list;
            }
        }
    }
}


function refreshDrawWeibos(select_name, weibos_obj){
    // var select_name = 'happy';
    $("#weibo_list").empty();
    if (!select_name in weibos_obj){
        $("#weibo_list").append('<li class="item">关键微博为空！</li>');
        return;
    }

    var data = weibos_obj[select_name];
    var html = "";
    html += '<div class="tang-scrollpanel-wrapper" style="height: ' + 66 * data.length  + 'px;">';
    html += '<div class="tang-scrollpanel-content">';
    html += '<ul id="weibo_ul">';
    for(var i = 0; i < data.length; i += 1){
        var emotion = select_name;
        var da = data[i];
        var uid = da['user'];
        var name;
        if ('name' in da){
            name = da['name'];
            if(name == 'unknown'){
                name = '未知';
            }
        }
        else{
            name = '未知';
        }
        var mid = da['_id'];
        var retweeted_mid = da['retweeted_mid'];
        var retweeted_uid = da['retweeted_uid'];
        var ip = da['geo'];
        var loc = ip;
        var text = da['text'];
        var reposts_count = da['reposts_count'];
        var comments_count = da['comments_count'];
        var timestamp = da['timestamp'];
        var date = new Date(timestamp * 1000).format("yyyy年MM月dd日 hh:mm:ss");
        var weibo_link = da['weibo_link'];
        var user_link = 'http://weibo.com/u/' + uid;
        var user_image_link = da['profile_image_url'];
        if (user_image_link == 'unknown'){
            user_image_link = '/static/img/unknown_profile_image.gif';
        }
        html += '<li class="item"><div class="weibo_face"><a target="_blank" href="' + user_link + '">';
        html += '<img src="' + user_image_link + '">';
        html += '</a></div>';
        html += '<div class="weibo_detail">';
        html += '<p>昵称:<a class="undlin" target="_blank" href="' + user_link  + '">' + name + '</a>&nbsp;&nbsp;UID:' + uid + '&nbsp;&nbsp;于' + ip + '&nbsp;&nbsp;发布&nbsp;&nbsp;' + text + '</p>';
        html += '<div class="weibo_info">';
        html += '<div class="weibo_pz">';
        html += '<a class="undlin" href="javascript:;" target="_blank">转发(' + reposts_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
        html += '<a class="undlin" href="javascript:;" target="_blank">评论(' + comments_count + ')</a></div>';
        html += '<div class="m">';
        html += '<a class="undlin" target="_blank" href="' + weibo_link + '">' + date + '</a>&nbsp;-&nbsp;';
        html += '<a target="_blank" href="http://weibo.com">新浪微博</a>&nbsp;-&nbsp;';
        html += '<a target="_blank" href="' + weibo_link + '">微博页面</a>&nbsp;-&nbsp;';
        html += '<a target="_blank" href="' + user_link + '">用户页面</a>';
        html += '</div>';
        html += '</div>';
        html += '</div>';
        html += '</li>';
    }
    html += '</ul>';
    html += '</div>';
    html += '<div id="TANGRAM_54__slider" class="tang-ui tang-slider tang-slider-vtl" style="height: 100%;">';
    html += '<div id="TANGRAM_56__view" class="tang-view" style="width: 6px;">';
    html += '<div class="tang-content">';
    html += '<div id="TANGRAM_56__inner" class="tang-inner">';
    html += '<div id="TANGRAM_56__process" class="tang-process tang-process-undefined" style="height: 0px;">';
    html += '</div>';
    html += '</div>';
    html += '</div>';
    html += '<a id="TANGRAM_56__knob" href="javascript:;" class="tang-knob" style="top: 0%; left: 0px;"></a>';
    html += '</div>';
    html += '<div class="tang-corner tang-start" id="TANGRAM_54__arrowTop"></div>';
    html += '<div class="tang-corner tang-last" id="TANGRAM_54__arrowBottom"></div>';
    html += '</div>';
    $("#weibo_list").append(html);
}

// instance method, 初始化绘制关键微博列表
TrendsLine.prototype.initDrawWeibos = function(){
    var weibos_obj = this.range_weibos_data;
    var select_name = 'happy';
    refreshDrawWeibos(select_name, weibos_obj);
    bindSentimentTabClick(weibos_obj);
}

function bindSentimentTabClick(weibos_obj){
    $("#sentimentTabDiv").children("a").unbind();
    $("#sentimentTabDiv").children("a").click(function() {
        var select_a = $(this);
        var unselect_a = $(this).siblings('a');
        if(!select_a.hasClass('curr')) {
            select_a.addClass('curr');
            unselect_a.removeClass('curr');
            var select_sentiment = select_a.attr('sentiment');
            refreshDrawWeibos(select_sentiment, weibos_obj);
        }
    });
}

// instance method, 获取数据并绘制趋势图
TrendsLine.prototype.pullDrawTrend = function(){
    var trends_title = this.trend_title;
    var names = this.names;

    var trend_div_id = this.trend_div_id;
    var pointInterval = this.pointInterval;
    var start_ts = this.start_ts;
    var end_ts = this.end_ts;
    var xAxisTitleText = '时间';
    var yAxisTitleText = '数量';
    var series_data = [{
            name: '高兴',
            data: [],
            id: 'happy',
            color: '#11c897',
            marker : {
                enabled : false,
            }
        },{
            name: '愤怒',
            data: [],
            id: 'angry',
            color: '#fa7256',
            marker : {
                enabled : false,
            }
        },{
            name: '悲伤',
            data: [],
            id: 'sad',
            color: '#6e87d7',
            marker : {
                enabled : false,
            }
        },{
            name: '拐点-高兴',
            type : 'flags',
            data : [],
            cursor: 'pointer',
            onSeries : 'happy',
            shape : 'circlepin',
            width : 2,
            color: '#11c897',
            visible: false, // 默认显示绝对
            showInLegend: false
        },{
            name: '拐点-愤怒',
            type : 'flags',
            data : [],
            cursor: 'pointer',
            onSeries : 'angry',
            shape : 'circlepin',
            width : 2,
            color: '#fa7256',
            visible: false, // 默认显示绝对
            showInLegend: false
        },{
            name: '拐点-悲伤',
            type : 'flags',
            data : [],
            cursor: 'pointer',
            onSeries : 'sad',
            shape : 'circlepin',
            width : 2,
            color: '#6e87d7',
            visible: false, // 默认显示绝对
            showInLegend: false
        },{
            name: '拐点-高兴',
            type : 'flags',
            data : [],
            cursor: 'pointer',
            onSeries : 'happy',
            shape : 'circlepin',
            width : 2,
            color: '#11c897',
            visible: true, // 默认显示绝对
            showInLegend: true
        },{
            name: '拐点-愤怒',
            type : 'flags',
            data : [],
            cursor: 'pointer',
            onSeries : 'angry',
            shape : 'circlepin',
            width : 2,
            color: '#fa7256',
            visible: true, // 默认显示绝对
            showInLegend: true
        },{
            name: '拐点-悲伤',
            type : 'flags',
            data : [],
            cursor: 'pointer',
            onSeries : 'sad',
            shape : 'circlepin',
            width : 2,
            color: '#6e87d7',
            visible:true, // 默认显示绝对
            showInLegend: true
        }]

    var that = this;
    myChart = display_trend(that, trend_div_id, this.query, pointInterval, start_ts, end_ts, trends_title, series_data, xAxisTitleText, yAxisTitleText);
    this.trend_chart = myChart;

    $("[name='abs_rel_switch']").on('switchChange.bootstrapSwitch', function(event, state) {
        var chart = $('#trend_div').highcharts();
        var yAxis = chart.yAxis[0];
        if (state == false){
            yAxis.update({
                max: 1
            });
            for (var i in chart.series){
                var series = chart.series[i];
                if(i == 0 || i == 1 || i == 2){
                    var name;
                    if (i == 0){
                        name = 'happy';
                    }
                    else if(i == 1){
                        name = 'angry';
                    }
                    else if(i == 2){
                        name = 'sad';
                    }
                    series.update({
                        data: that.trend_count_obj['ratio'][name]
                    });
                }
                else if (i == 3 || i == 4 || i == 5){
                    series.update({
                        showInLegend: true
                    });
                    series.show();
                }
                else if (i == 6 || i == 7 || i == 8){
                    series.update({
                        showInLegend: false
                    })
                    series.hide();
                }
            }
        }
        else{
            yAxis.update({
                max: null
            });
            for (var i in chart.series){
                var series = chart.series[i];
                if(i == 0 || i == 1 || i == 2){
                    var name;
                    if (i == 0){
                        name = 'happy';
                    }
                    else if(i == 1){
                        name = 'angry';
                    }
                    else if(i == 2){
                        name = 'sad';
                    }
                    series.update({
                        data: that.trend_count_obj['count'][name]
                    });
                }
                else if (i == 3 || i == 4 || i == 5){
                    series.update({
                        showInLegend: false
                    });
                    series.hide();
                }
                else if (i == 6 || i == 7 || i == 8){
                    series.update({
                        showInLegend: true
                    })
                    series.show();
                }
            }
        }
    });
}


function pull_emotion_count(that, query, emotion_type, total_days, times, begin_ts, during, count_series, relative_peak_series, absolute_peak_series){
    var names = that.names;

    if(times > total_days){
        get_peaks(that, relative_peak_series, that.trend_count_obj['ratio'], that.trend_count_obj['ts'], during);
        get_peaks(that, absolute_peak_series, that.trend_count_obj['count'], that.trend_count_obj['ts'], during);
        $("[name='abs_rel_switch']").bootstrapSwitch('readonly', false);
        return;
    }

    var ts = begin_ts + times * during;
    var ajax_url = "/moodlens/data/?ts=" + ts + '&during=' + during + '&emotion=' + emotion_type + '&query=' + query;
    $.ajax({
        url: ajax_url,
        type: "GET",
        dataType:"json",
        success: function(data){
            var isShift = false;
            var total_count = 0;
            var count_obj = {};
            for(var name in names){
                if(name in data){
                    var count = data[name][1];
                    count_obj[name] = count;
                    total_count += count;
                }
            }
            that.trend_count_obj['ts'].push(ts);
            if(total_count > 0){
                for(var name in count_obj){
                    var count = count_obj[name];
                    var ratio = parseInt(count * 10000 / total_count) / 10000.0;
                    count_series[name].addPoint([ts * 1000, count], true, isShift);
                    that.trend_count_obj['count'][name].push([ts * 1000, count]);
                    that.trend_count_obj['ratio'][name].push([ts * 1000, ratio]);
                }
            }
            else{
                for(var name in count_obj){
                    count_series[name].addPoint([ts * 1000, 0], true, isShift);
                    that.trend_count_obj['count'][name].push([ts * 1000, 0]);
                    that.trend_count_obj['ratio'][name].push([ts * 1000, 0.0]);
                }
            }
            times++;
            pull_emotion_count(that, query, emotion_type, total_days, times, begin_ts, during, count_series, relative_peak_series, absolute_peak_series);
        }
    });
}

function display_trend(that, trend_div_id, query, during, begin_ts, end_ts, trends_title, series_data, xAxisTitleText, yAxisTitleText){
    Highcharts.setOptions({
        global: {
            useUTC: false
        }
    });


    var names = that.names;

    var chart_obj = $('#' + trend_div_id).highcharts({
        chart: {
            type: 'spline',// line,
            animation: Highcharts.svg, // don't animate in old IE
            style: {
                fontSize: '12px',
                fontFamily: 'Microsoft YaHei'
            },
            events: {
                load: function() {
                    var total_nodes = (end_ts - begin_ts) / during;
                    var times_init = 0;

                    var count_series = {};
                    var relative_peak_series = {};
                    var absolute_peak_series = {};
                    var idx = 0;
                    for(var name in names){
                        count_series[name] = this.series[idx];
                        relative_peak_series[name] = this.series[idx+3];
                        absolute_peak_series[name] = this.series[idx+6];
                        idx += 1;
                    }
                    pull_emotion_count(that, query, 'global', total_nodes, times_init, begin_ts, during, count_series, relative_peak_series, absolute_peak_series);
                }
            }
        },
        plotOptions:{
            line:{
                events: {
                    legendItemClick: function () {
                        /*
                        var seriesIndex = this.index;
                        series_flag[seriesIndex] = - series_flag[seriesIndex];
                        if(seriesIndex <= 2){
                            if(status_flag == 'absolute'){
                                if(series_flag[seriesIndex] != series_flag[seriesIndex+6]){
                                    $(this.chart.series[seriesIndex+6].legendItem.element).trigger('click');
                                }
                            }
                            else{
                                if (series_flag[seriesIndex] != series_flag[seriesIndex+3]){
                                    $(this.chart.series[seriesIndex+3].legendItem.element).trigger('click');
                                }
                            }
                        }*/
                    }
                }
            }
        },
        title : {
            text: '走势分析图', // trends_title
            margin: 20,
            style: {
                color: '#666',
                fontWeight: 'bold',
                fontSize: '14px',
                fontFamily: 'Microsoft YaHei'
            }
        },
        // 导出按钮汉化
        lang: {
            printChart: "打印",
            downloadJPEG: "下载JPEG 图片",
            downloadPDF: "下载PDF文档",
            downloadPNG: "下载PNG 图片",
            downloadSVG: "下载SVG 矢量图",
            exportButtonTitle: "导出图片"
        },
        rangeSelector: {
            selected: 4,
            inputEnabled: false,
            buttons: [{
                type: 'week',
                count: 1,
                text: '1w'
            }, {
                type: 'month',
                count: 1,
                text: '1m'
            }, {
                type: 'month',
                count: 3,
                text: '3m'
            }]
        },
        xAxis: {
            title: {
                enabled: true,
                text: xAxisTitleText,
                style: {
                    color: '#666',
                    fontWeight: 'bold',
                    fontSize: '12px',
                    fontFamily: 'Microsoft YaHei'
                }
            },
            type: 'datetime',
            tickPixelInterval: 150
        },
        yAxis: {
            min: 0,
            title: {
                enabled: true,
                text: yAxisTitleText,
                style: {
                    color: '#666',
                    fontWeight: 'bold',
                    fontSize: '12px',
                    fontFamily: 'Microsoft YaHei'
                }
            },
        },
        tooltip: {
            valueDecimals: 2,
            xDateFormat: '%Y-%m-%d %H:%M:%S'
        },
        legend: {
            layout: 'horizontal',
            //verticalAlign: true,
            //floating: true,
            align: 'center',
            verticalAlign: 'bottom',
            x: 0,
            y: -2,
            borderWidth: 1,
            itemStyle: {
                color: '#666',
                fontWeight: 'bold',
                fontSize: '12px',
                fontFamily: 'Microsoft YaHei'
            }
            //enabled: true,
            //itemHiddenStyle: {
                //color: 'white'
            //}
        },
        exporting: {
            enabled: true
        },
        series: series_data
    });
    return chart_obj;
}


function call_peak_ajax(that, series, data_list, ts_list, during, emotion){
    var names = that.names;

    var data = [];
    for(var i in data_list){
        data.push(data_list[i][1]);
    }

    var min_keywords_size = that.min_keywords_size;
    var max_keywords_size = that.max_keywords_size;

    var ajax_url = that.peak_ajax_url(data, ts_list, during, emotion);
    var pie_title = that.pie_title;
    var pie_series_title = that.pie_series_title;
    var legend_data = [];
    for (var name in names){
        legend_data.push(names[name]);
    }
    var pie_div_id = that.pie_div_id;

    that.call_async_ajax_request(ajax_url, that.ajax_method, peak_callback);

    function peak_callback(data){
        if ( data != 'Null Data'){
            var isShift = false;
            for(var i in data){
                var x = data[i]['ts'];
                var title = data[i]['title'];
                series.addPoint({'x': x, 'title': title, 'text': title, 'emotion': emotion, 'events': {'click': flagClick}}, true, isShift);
                var flagClick = function(event){
                    var click_ts = this.x / 1000;
                    var emotion = this.emotion;
                    var title = this.title;

                    peakDrawTip(click_ts, emotion, title);
                    peakPullDrawKeywords(click_ts, emotion, title);
                    peakPullDrawPie(click_ts, emotion, title);
                    peakPullDrawWeibos(click_ts, emotion, title);
                }
            }
        }
    }

    function peakDrawTip(click_ts, emotion, title){
        $("#peak_trend_tooltip").empty();
        $("#peak_trend_tooltip").append('<span>当前点击了点' + title + '&nbsp;&nbsp;情绪:' + that.names[emotion] + '&nbsp;&nbsp;日期:' + new Date(click_ts * 1000).format("yyyy年MM月dd日 hh:mm:ss") + '</span>');
        $("#peak_cloudpie_tooltip").empty();
        $("#peak_cloudpie_tooltip").append('<span>当前点击了点' + title + '&nbsp;&nbsp;情绪:' + that.names[emotion] + '&nbsp;&nbsp;日期:' + new Date(click_ts * 1000).format("yyyy年MM月dd日 hh:mm:ss") + '</span>');
        $("#peak_weibo_tooltip").empty();
        $("#peak_weibo_tooltip").append('<span>当前点击了点' + title + '&nbsp;&nbsp;情绪:' + that.names[emotion] + '&nbsp;&nbsp;日期:' + new Date(click_ts * 1000).format("yyyy年MM月dd日 hh:mm:ss") + '</span>');
    }

    function peakPullDrawKeywords(click_ts, emotion, title){
        var ajax_url = that.keywords_ajax_url(that.query, click_ts, that.pointInterval, emotion);
        that.call_async_ajax_request(ajax_url, that.ajax_method, callback);
        function callback(data){
            refreshDrawKeywords(min_keywords_size, max_keywords_size, data[emotion], emotion);
        }
    }

    function peakPullDrawPie(click_ts, emotion, title){
        var ajax_url = that.pie_ajax_url(that.query, click_ts, that.pointInterval);
        that.call_async_ajax_request(ajax_url, that.ajax_method, callback);
        function callback(data){
            var pie_data = [];
            for (var status in data){
                var count = data[status];
                pie_data.push({
                    value: count,
                    name: names[status]
                })
            }
            refreshDrawPie(pie_data, pie_title, pie_series_title, legend_data, pie_div_id);
        }
    }

    function peakPullDrawWeibos(click_ts, emotion, title){
        var ajax_url = that.weibos_ajax_url(that.query, click_ts, that.pointInterval, 'global', that.top_weibos_limit);
        that.call_async_ajax_request(ajax_url, that.ajax_method, callback);
        function callback(data){
            refreshWeiboTab(emotion);
            refreshDrawWeibos(emotion, data);
            bindSentimentTabClick(data);
        }
    }

    function refreshWeiboTab(emotion){
        $("#sentimentTabDiv").children("a").each(function() {
            var select_a = $(this);
            var select_a_sentiment = select_a.attr('sentiment');
            if (select_a_sentiment == emotion){
                if(!select_a.hasClass('curr')) {
                    select_a.addClass('curr');
                }
            }
            else{
                if(select_a.hasClass('curr')) {
                    select_a.removeClass('curr');
                }
            }
        });
    }
}

function get_peaks(that, series, data_obj, ts_list, during){
    var names = that.names;
    for (var name in names){
        var select_series = series[name];
        var data_list = data_obj[name];
        call_peak_ajax(that, select_series, data_list, ts_list, during, name);
    }
}

//(function keywords_cloud_load(){
    var radius = 85;
    var dtr = Math.PI/180;
    var d=300;

    var mcList = [];
    var active = false;
    var lasta = 1;
    var lastb = 1;
    var distr = true;
    var tspeed=2;
    var size=250;

    var mouseX=0;
    var mouseY=0;

    var howElliptical=1;

    var aA=null;
    var oDiv=null;
    function on_load()
    {
        var i=0;
        var oTag=null;
        mcList = [];

        oDiv=document.getElementById('keywords_cloud_div');

        aA=oDiv.getElementsByTagName('a');

        for(i=0;i<aA.length;i++)
        {
            oTag={};

            oTag.offsetWidth=aA[i].offsetWidth;
            oTag.offsetHeight=aA[i].offsetHeight;

            mcList.push(oTag);
        }

        sineCosine( 0,0,0 );

        positionAll();

        oDiv.onmouseover=function ()
        {
            active=true;
        };

        oDiv.onmouseout=function ()
        {
            active=false;
        };

        oDiv.onmousemove=function (ev)
        {
            var oEvent=window.event || ev;

            mouseX=oEvent.clientX-(oDiv.offsetLeft+oDiv.offsetWidth/2);
            mouseY=oEvent.clientY-(oDiv.offsetTop+oDiv.offsetHeight/2);

            mouseX/=5;
            mouseY/=5;
        };

        setInterval(update, 30);
    };

    function update()
    {
        var a;
        var b;

        if(active)
        {
            a = (-Math.min( Math.max( -mouseY, -size ), size ) / radius ) * tspeed;
            b = (Math.min( Math.max( -mouseX, -size ), size ) / radius ) * tspeed;
        }
        else
        {
            a = lasta * 0.98;
            b = lastb * 0.98;
        }

        lasta=a;
        lastb=b;

        if(Math.abs(a)<=0.01 && Math.abs(b)<=0.01)
        {
            return;
        }

        var c=0;
        sineCosine(a,b,c);
        for(var j=0;j<mcList.length;j++)
        {
            var rx1=mcList[j].cx;
            var ry1=mcList[j].cy*ca+mcList[j].cz*(-sa);
            var rz1=mcList[j].cy*sa+mcList[j].cz*ca;

            var rx2=rx1*cb+rz1*sb;
            var ry2=ry1;
            var rz2=rx1*(-sb)+rz1*cb;

            var rx3=rx2*cc+ry2*(-sc);
            var ry3=rx2*sc+ry2*cc;
            var rz3=rz2;

            mcList[j].cx=rx3;
            mcList[j].cy=ry3;
            mcList[j].cz=rz3;

            per=d/(d+rz3);

            mcList[j].x=(howElliptical*rx3*per)-(howElliptical*2);
            mcList[j].y=ry3*per;
            mcList[j].scale=per;
            mcList[j].alpha=per;

            mcList[j].alpha=(mcList[j].alpha-0.6)*(10/6);
        }

        doPosition();
        depthSort();
    }

    function depthSort()
    {
        var i=0;
        var aTmp=[];

        for(i=0;i<aA.length;i++)
        {
            aTmp.push(aA[i]);
        }

        aTmp.sort
        (
            function (vItem1, vItem2)
            {
                if(vItem1.cz>vItem2.cz)
                {
                    return -1;
                }
                else if(vItem1.cz<vItem2.cz)
                {
                    return 1;
                }
                else
                {
                    return 0;
                }
            }
        );

        for(i=0;i<aTmp.length;i++)
        {
            aTmp[i].style.zIndex=i;
        }
    }

    function positionAll()
    {
        var phi=0;
        var theta=0;
        var max=mcList.length;

        var i=0;
        var aTmp=[];
        var oFragment=document.createDocumentFragment();

        //随机排序
        for(i=0;i<aA.length;i++)
        {
            aTmp.push(aA[i]);
        }

        aTmp.sort
        (
            function ()
            {
                return Math.random()<0.5?1:-1;
            }
        );

        for(i=0;i<aTmp.length;i++)
        {
            oFragment.appendChild(aTmp[i]);
        }

        oDiv.appendChild(oFragment);

        for( var i=1; i<max+1; i++){
            if( distr )
            {
                phi = Math.acos(-1+(2*i-1)/max);
                theta = Math.sqrt(max*Math.PI)*phi;
            }
            else
            {
                phi = Math.random()*(Math.PI);
                theta = Math.random()*(2*Math.PI);
            }

            //坐标变换
            mcList[i-1].cx = radius * Math.cos(theta)*Math.sin(phi);
            mcList[i-1].cy = radius * Math.sin(theta)*Math.sin(phi);
            mcList[i-1].cz = radius * Math.cos(phi);

            aA[i-1].style.left=mcList[i-1].cx+oDiv.offsetWidth/2-mcList[i-1].offsetWidth/2+'px';
            aA[i-1].style.top=mcList[i-1].cy+oDiv.offsetHeight/2-mcList[i-1].offsetHeight/2+'px';
        }
    }

    function doPosition()
    {
        var l=oDiv.offsetWidth/2;
        var t=oDiv.offsetHeight/2;
        for(var i=0;i<mcList.length;i++)
        {
            aA[i].style.left=mcList[i].cx+l-mcList[i].offsetWidth/2+'px';
            aA[i].style.top=mcList[i].cy+t-mcList[i].offsetHeight/2+'px';

            aA[i].style.ontSize=Math.ceil(12*mcList[i].scale/2)+8+'px';

            aA[i].style.filter="alpha(opacity="+100*mcList[i].alpha+")";
            aA[i].style.opacity=mcList[i].alpha;
        }
    }

    function sineCosine( a, b, c)
    {
        sa = Math.sin(a * dtr);
        ca = Math.cos(a * dtr);
        sb = Math.sin(b * dtr);
        cb = Math.cos(b * dtr);
        sc = Math.sin(c * dtr);
        cc = Math.cos(c * dtr);
    }
//})();

/*
var START_TS = 1377964800;
var END_TS = 1378051200;
var DURING_INTERGER = 60 * 60;
*/

tl = new TrendsLine(QUERY, START_TS, END_TS, POINT_INTERVAL)
tl.pullDrawTrend();
tl.initPullDrawPie();
tl.initPullDrawKeywords();
tl.initPullWeibos();
tl.initDrawWeibos();

