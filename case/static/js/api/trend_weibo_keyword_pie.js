/* trends */

// TrendsLine Constructor
function TrendsLine(start_ts, end_ts, pointInterval){
    //instance property
    this.query = '中国';
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
    this.range_count_data = {};
    this.range_keywords_data = {};
    this.range_weibos_data = [];
    this.top_keywords_limit = 50;
    this.top_weibos_limit = 5;
    this.max_keywords_size = 50;
    this.min_keywords_size = 2;
    this.pie_title = '情绪饼图';
    this.pie_series_title = '情绪占比';
    this.pie_div_id = 'pie_div';
    this.trend_div_id = 'trend_div';
    this.trend_title = '情绪走势图';
    this.trend_chart;

    var names = {
        'happy': '高兴',
        'sad': '悲伤',
        'angry': '愤怒'
    }

    this.trend_count_obj = {
        'ts': [], // 时间数组
        'count': {},
        'ratio': {}
    };

    for (var name in names){
        this.trend_count_obj['count'][name] = [];
        this.trend_count_obj['ratio'][name] = [];
    }
}

// instance method, 初始化时获取整个时间段的count数据
TrendsLine.prototype.pullRangeCount = function(){
    var ajax_url = this.pie_ajax_url(this.query, this.end_ts, this.during);

    that = this;
    this.call_sync_ajax_request(ajax_url, this.ajax_method, range_count_callback);

    function range_count_callback(data){
        that.range_count_data = data;
    }
}

// instance method, 画饼图
TrendsLine.prototype.drawPie = function(){
    var names = {
        'happy': '高兴',
        'sad': '悲伤',
        'angry': '愤怒'
    }

    var pie_data = [];
    for (var status in this.range_count_data){
        var count = this.range_count_data[status];
        pie_data.push({
            value: count,
            name: names[status]
        })
    }

    var pie_title = this.pie_title;
    var pie_series_title = this.pie_series_title;
    var legend_data = [];
    for (var name in names){
        legend_data.push(names[name]);
    }
    var pie_div_id = this.pie_div_id;

    var option = {
        backgroundColor: '#F0F0F0',
        title : {
            text: pie_title,
            x: 'center',
            textStyle:{
                fontWeight: 'lighter',
                fontSize: 13
            }
        },
        tooltip : {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)"
        },
        legend: {
            orient:'vertical',
            x : 'left',
            data: legend_data
        },

        calculable : true,
        series : [
            {
                name: this.pie_series_title,
                type: 'pie',
                radius : '50%',
                center: ['50%', '60%'],
                data: pie_data
            }
        ]
    };
    var myChart = echarts.init(document.getElementById(pie_div_id));
    myChart.setOption(option);
}

// instance method, 拉取时间范围关键词云数据
TrendsLine.prototype.pullRangeKeywords = function(){
    var names = {
        'happy': '高兴',
        'sad': '悲伤',
        'angry': '愤怒'
    }
    var keywords_data = [];
    that = this;
    for (var name in names){
        var ajax_url = this.keywords_ajax_url(this.query, this.end_ts, this.during, name);
        this.call_sync_ajax_request(ajax_url, this.ajax_method, range_keywords_callback);
    }
    function range_keywords_callback(data){
        for(var name in names){
            if(name in data){
                var keywords_count_obj = data[name];
                for (var keyword in keywords_count_obj){
                    if (keyword in that.range_keywords_data){
                        that.range_keywords_data[keyword] += keywords_count_obj[keyword];
                    }
                    else{
                        that.range_keywords_data[keyword] = keywords_count_obj[keyword];
                    }
                }
            }
        }
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

// instance method, 画关键词云图
TrendsLine.prototype.drawKeywords = function(){
    if (this.range_keywords_data == {}){
        $("#keywords_cloud_div").empty();
        $("#keywords_cloud_div").append("<a style='font-size:1ex'>关键词云数据为空</a>");
    }
    else{
        $("#keywords_cloud_div").empty();
        var min_count, max_count = 0;
        var idx = 0;
        var words_count_obj = {};
        for (var keyword in this.range_keywords_data){
            var count = this.range_keywords_data[keyword];
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
            if(idx == this.top_keywords_limit){
                break
            }
            idx += 1;
        }
        for(var keyword in words_count_obj){
            var count = words_count_obj[keyword];
            var size = defscale(count, min_count, max_count, this.min_keywords_size, this.max_keywords_size);
            $('#keywords_cloud_div').append("<a><font style=\"color:blue font-size:" + size + "\">" + keyword + "</font></a>");
        }
        on_load();
    }
}

// instance method, 初始化时获取关键微薄数据
TrendsLine.prototype.pullRangeWeibos = function(){
    var names = {
        'happy': '高兴',
        'sad': '悲伤',
        'angry': '愤怒'
    }
    var weibos_data = [];
    that = this;
    for (var name in names){
        var ajax_url = this.weibos_ajax_url(this.query, this.end_ts, this.during, name, this.top_weibos_limit);
        this.call_sync_ajax_request(ajax_url, this.ajax_method, range_weibos_callback);
    }

    function range_weibos_callback(data){
        that.range_weibos_data.push(data);
    };
}

// instance method, 画关键微薄列表
TrendsLine.prototype.drawWeibos = function(){
    var names = {
        'happy': '高兴',
        'sad': '悲伤',
        'angry': '愤怒'
    }
    $("#vertical-ticker").empty();
    var select_name = 'happy';
    var select_weibo_list = [];
    for(var idx in this.range_weibos_data){
        var weibos_list = this.range_weibos_data[idx];
        for(var name in names){
            if(name in weibos_list && name == select_name){
                select_weibo_list = weibos_list[name];
            }
        }
    }

    if(select_weibo_list.length == 0){
        $("#vertical-ticker").append("关键微博为空！");
    }
    else{
        var html = "";
        var data = select_weibo_list;
        for(var i = 0; i < data.length; i += 1){
            var emotion = select_name;
            var name = data[i]['user'];
            var user_link = 'http://weibo.com/u/'+data[i]['user'];
            var text = data[i]['text'];
            var weibo_link = data[i]['weibo_link'];
            var repost_count = data[i]['reposts_count'];
            var retweeted_text = 'None';
            html += "<div class=\"chartclient-annotation-letter\"><img src='/static/img/" + emotion + "_thumb.gif'></div>"; 
            html += "<div class=\"chartclient-annotation-title\"><a href='" + user_link + "' target='_blank' >" + name + "</a> 发布 </div>";
            html += "<div class=\"chartclient-annotation-content\"><a href='" + weibo_link + "' target='_blank' >" + text + "</a></div>";
            if(retweeted_text != 'None'){
                html += "<div class=\"chartclient-annotation-content\">" + retweeted_text + "</div>";
            }
            html += "<div class=\"chartclient-annotation-date\"><span style=\"float:right\"> 转发数：" +  repost_count + "</span></div>";
        }
        $("#vertical-ticker").append(html);
    }
}

// instance method, 获取趋势图数据
TrendsLine.prototype.pullDrawPointCount = function(){
    var names = {
        'happy': '高兴',
        'sad': '悲伤',
        'angry': '愤怒'
    }
    var points_number = this.during / this.pointInterval + 1;
    var trends_title = this.trend_title;
    var legend_data = [];
    for (var name in names){
        legend_data.push(names[name]);
        this.trend_count_obj[name] = [];
    }
    this.trend_count_obj['ts'] = [];

    that = this;

    for (var iters = 0; iters < points_number; iters += 1){
        var end_ts = this.start_ts + (iters + 1) * this.pointInterval;
        this.trend_count_obj['ts'].push(end_ts);
        for (var name in names){
            var ajax_url = this.count_ajax_url(this.query, end_ts, this.pointInterval, name);
            this.call_sync_ajax_request(ajax_url, this.ajax_method, point_count_callback);
        }
    }

    function point_count_callback(data){
            for (var name in names){
                if(name in data){
                    that.trend_count_obj[name].push(data[name][1]);
                }
            }
            var xAxis_data = that.trend_count_obj['ts'];
            var series_data = [];
            for(var name in that.trend_count_obj){
                if(that.trend_count_obj[name].length != 0){
                series_data.push({
                    name: name,
                    type: 'line',
                    data: that.trend_count_obj[name]
                });
                }
            }
            var option = init_option(xAxis_data, series_data)
            that.trend_chart.setOption(option);
    }
}

// instance method, 初始化走势图
TrendsLine.prototype.initDrawTrend = function(){
    var trends_title = this.trend_title;
    var names = {
        'happy': '高兴',
        'sad': '悲伤',
        'angry': '愤怒'
    }
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
            color: '#006600',
            marker : {
                enabled : false,
            }
        },{
            name: '愤怒',
            data: [],
            id: 'angry',
            color: '#FF0000',
            marker : {
                enabled : false,
            }
        },{
            name: '悲伤',
            data: [],
            id: 'sad',
            color: '#000099',
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
            color: '#006600'
        },{
            name: '拐点-愤怒',
            type : 'flags',
            data : [],
            cursor: 'pointer',
            onSeries : 'angry',
            shape : 'circlepin',
            width : 2,
            color: '#FF0000'
        },{
            name: '拐点-悲伤',
            type : 'flags',
            data : [],
            cursor: 'pointer',
            onSeries : 'sad',
            shape : 'circlepin',
            width : 2,
            color: '#000099'
        },{
            name: '拐点-高兴',
            type : 'flags',
            data : [],
            cursor: 'pointer',
            onSeries : 'happy',
            shape : 'circlepin',
            width : 2,
            color: '#006600',
            visible:false, // 默认显示相对
            showInLegend: false
        },{
            name: '拐点-愤怒',
            type : 'flags',
            data : [],
            cursor: 'pointer',
            onSeries : 'angry',
            shape : 'circlepin',
            width : 2,
            color: '#FF0000',
            visible:false, // 默认显示相对
            showInLegend: false
        },{
            name: '拐点-悲伤',
            type : 'flags',
            data : [],
            cursor: 'pointer',
            onSeries : 'sad',
            shape : 'circlepin',
            width : 2,
            color: '#000099',
            visible:false, // 默认显示相对
            showInLegend: false
        }]

    var that = this;
    myChart = display_trend(that, trend_div_id, this.query, pointInterval, start_ts, end_ts, trends_title, series_data, xAxisTitleText, yAxisTitleText);
    this.trend_chart = myChart;

    $("#absolute_label").click(function() {
        var click_flag = true;
        if(click_flag){
            var chart = $('#trend_div').highcharts();
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
        else{
            alert("请等待相对曲线加载完毕！");
        }
    });

    $("#relative_label").click(function() {
        var chart = $('#trend_div').highcharts();
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
    });
}

var START_TS = 1377964800;
var END_TS = 1378051200;
var DURING_INTERGER = 15 * 60;
tl = new TrendsLine(START_TS, END_TS, DURING_INTERGER)
tl.pullRangeCount()
tl.drawPie();
tl.pullRangeKeywords();
tl.drawKeywords();
tl.pullRangeWeibos();
tl.drawWeibos();
tl.initDrawTrend();
//tl.pullDrawPointCount();

function pull_emotion_count(that, query, emotion_type, total_days, times, begin_ts, during, count_series, relative_peak_series, absolute_peak_series){
    var names = {
        'happy': '高兴',
        'sad': '悲伤',
        'angry': '愤怒'
    }
    if(times > total_days){
        get_peaks(relative_peak_series, that.trend_count_obj['ratio'], that.trend_count_obj['ts'], during);
        get_peaks(absolute_peak_series, that.trend_count_obj['count'], that.trend_count_obj['ts'], during);
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
                    count_series[name].addPoint([ts * 1000, ratio], true, isShift);
                    that.trend_count_obj['count'][name].push([ts * 1000, count]);
                    that.trend_count_obj['ratio'][name].push([ts * 1000, ratio]);
                }
            }
            else{
                for(var name in count_obj){
                    count_series[name].addPoint([ts * 1000, 0.0], true, isShift);
                    that.trend_count_obj['count'][name].push([ts * 1000, 0]);
                    that.trend_count_obj['ratio'][name].push([ts * 1000, 0.0]);
                }
            }
            times++;
            pull_emotion_count(that, query, emotion_type, total_days, times, begin_ts, during, count_series, relative_peak_series, absolute_peak_series);
        }
    });
    //预防用户在series加载完毕前，变换相对绝对。
    document.getElementById("relative").checked="checked";
}

function display_trend(that, trend_div_id, query, during, begin_ts, end_ts, trends_title, series_data, xAxisTitleText, yAxisTitleText){
    Highcharts.setOptions({
        global: {
            useUTC: false
        }
    });


    var names = {
        'happy': '高兴',
        'sad': '悲伤',
        'angry': '愤怒'
    }

    var chart_obj = $('#' + trend_div_id).highcharts({
        chart: {
            type: 'spline',// line,
            animation: Highcharts.svg, // don't animate in old IE
            //marginTop: 20,
            marginRight: 10,
            //marginLeft: 10,
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
            text: trends_title
        },
        // 导出按钮汉化
        lang: {
            printButtonTitle: "打印",
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
                text: xAxisTitleText
            },
            type: 'datetime',
            tickPixelInterval: 150
        },
        yAxis: {
            min: 0,
            title: {
                text: yAxisTitleText
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
            align: 'center', //'right',
            verticalAlign: 'bottom',
            x: 0,
            y: -2,
            borderWidth: 1,
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


function call_peak_ajax(series, data_list, ts_list, during, emotion){
    var data = [];
    for(var i in data_list){
        data.push(data_list[i][1]);
    }
    var ajax_url = "/moodlens/emotionpeak/?lis=" + data.join(',') + "&ts=" + ts_list + '&during=' + during + "&emotion=" + emotion;
    var ajax_method = "GET";
    $.ajax({
        url: ajax_url,
        type: ajax_method,
        dataType: "json",
        success: function(data){
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
                    }
                }
            }
        }
    })
}

/*
$.ajax({
    url: "/moodlens/weibos_data/" + emotion + "/global/?ts=" + click_ts + '&limit=' + WEIBOS_LIMIT + "&during=" + during,
    type: "GET",
    dataType:"json",
    success: function(data){
        $("#vertical-ticker").empty();
        $("#event_title").html(title);
        if(data[emotion].length>0){
            chg_weibos(data[emotion]);
        }
        else{
            $("#vertical-ticker").append(" 关键微博为空！");
        }
    }
});
$.ajax({
    url: "/moodlens/keywords_data/global/?ts=" + click_ts + "&emotion=" + emotion + "&limit=" + KEYWORDS_LIMIT + "&during=" + during,
    type: "GET",
    dataType:"json",
    success: function(data){
        if(data=='search function undefined'){
            $("#tags_ul").empty();
            $("#tags_ul").append("<li><a style='font-size:1ex'>关键词云数据为空</a></li>");
            redraw_tagcanvas();
        }
        else{
            if(isEmptyObject(data[emotion])){
                $("#tags_ul").empty();
                $("#tags_ul").append("<li><a style='font-size:1ex'>关键词云数据为空</a></li>");
                redraw_tagcanvas();
            }
            else{
                chg_tagcloud(data[emotion]);
            }
        }
    }
});
chg_emotion_pie(emotion_absolute[this.x]);
*/

function get_peaks(series, data_obj, ts_list, during){
    var names = {
        'happy': '高兴',
        'sad': '悲伤',
        'angry': '愤怒'
    }
    for (var name in names){
        var select_series = series[name];
        var data_list = data_obj[name];
        call_peak_ajax(select_series, data_list, ts_list, during, name);
    }
}

