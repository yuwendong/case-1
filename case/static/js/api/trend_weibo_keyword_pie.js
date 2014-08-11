var WEIBOS_LIMIT = 10;
var KEYWORDS_LIMIT = 10;
var click_flag=false;
var status_flag = 'relative';
var series_flag = [1, 1, 1, 1, 1, 1, -1, -1, -1]; //记录9个series选中与否的状态

var evolution_ratio = {};
var evolution_absolute={};

var axis_time=[];
var original_absolute = [];
var comment_absolute = [];
var forward_absolute = [];

var original_ratio = [];
var comment_ratio = [];
var forward_ratio = [];

var original_list = [];
var comment_list = [];
var forward_list = [];
var ts_list = [];

var original_alist = [];
var comment_alist = [];
var forward_alist = [];
var ts_alist = [];

/* trends */

// TrendsLine Constructor
function TrendsLine(start_ts, end_ts, pointInterval){
    //instance property
    this.query = '中国';
    this.start_ts = start_ts; // 开始时间戳
    this.end_ts = end_ts; // 终止时间戳
    this.pointInterval = pointInterval; // 图上一点的时间间隔
    this.during = end_ts - start_ts; // 整个时间范围
    this.count_ajax_url = function(query, end_ts, during){
        return "/moodlens/pie/?ts=" + end_ts + "&query=" + query + "&during=" + during;
    }
    this.keywords_ajax_url = function(query, end_ts, during, emotion){
        return "/moodlens/keywords_data/?ts=" + end_ts + "&query=" + query + "&during=" + during + "&emotion=" + emotion;
    }
    this.weibos_ajax_url = function(query, end_ts, during, emotion, limit){
        return "/moodlens/weibos_data/?query=" + query + "&ts=" + end_ts + "&during=" + during + "&limit=" + limit + "&emotion=" + emotion;
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
}

// instance method, 初始化时获取整个时间段的count数据
TrendsLine.prototype.pullRangeCount = function(){
    var ajax_url = this.count_ajax_url(this.query, this.end_ts, this.during);

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

/*
    function pull_evolution_count(total_days, times, begin_ts, during){   //请求数据
        if(times > total_days){
            return;
        }
        var ts = begin_ts + times * during;
        $.ajax({
            url: "/moodlens/data/?ts=" + ts + '&query=' + query,
            type: "GET",
            dataType:"json",
            async:false,
            success: function(data){
                var isShift = false;
                var original_evolution_count = data['original'];
                var comment_evolution_count = data['comment'];
                var forward_evolution_count = data['forward'];

                var total_evolution_count = original_evolution_count + comment_evolution_count + forward_evolution_count;
                if(total_evolution_count > 0){
                    var original_evolution_ratio = parseInt(original_evolution_count * 10000 / total_evolution_count) / 10000.0;
                    var comment_evolution_ratio = parseInt(comment_evolution_count * 10000 / total_evolution_count) / 10000.0;
                    var forward_evolution_ratio = parseInt(forward_evolution_count * 10000 / total_evolution_count) / 10000.0;

                    evolution_ratio[ts * 1000] = [original_evolution_ratio, comment_evolution_ratio, forward_evolution_ratio, total_evolution_count];
                    evolution_absolute[ts*1000]=[original_evolution_count, comment_evolution_count, forward_evolution_count, total_evolution_count];

                    original_absolute.push(original_evolution_count);
                    comment_absolute.push(comment_evolution_count);
                    forward_absolute.push(forward_evolution_count);


                    original_ratio.push(original_evolution_ratio);
                    comment_ratio.push(comment_evolution_ratio);
                    forward_ratio.push(forward_evolution_ratio);
                    axis_time.push(ts*1000);

                    original_list.push(original_evolution_ratio);
                    comment_list.push(comment_evolution_ratio);
                    forward_list.push(forward_evolution_ratio);
                    ts_list.push(ts);

                    original_alist.push(original_evolution_count);
                    comment_alist.push(comment_evolution_count);
                    forward_alist.push(forward_evolution_count);
                    ts_alist.push(ts);
                }

                else{
                    evolution_ratio[ts * 1000] = [0, 0, 0, 0];
                    evolution_absolute[ts*1000]= [0, 0, 0, 0];
                }

                times++;
                pull_evolution_count(total_days, times, begin_ts, during);
            }
        });
    }
*/
    /*
     * title_text: 图标题, '情绪走势图'
     * legend_data: legend的数组, 如['高兴', '愤怒', '悲伤']
     */
    var during = DURING_INTERGER;
    var begin_ts = START_TS;
    var end_ts = END_TS;
    var total_nodes = (end_ts - begin_ts) / during;
    var times_init = 0;
    // pull_evolution_count(total_nodes, times_init, begin_ts, during);
/*
    function display_trends(data, title_text, legend_data, trend_div_id){
        // series_data: option中series的值
        var series_data = [];
        var names = {
            '高兴': 'happy',
            '悲伤': 'sad',
            '愤怒': 'angry'
        }
        for (var d in data){
            var ratio = d;
            for(var name in names){
                series_data.push({
                    name: name, // '高兴'
                    type: 'line',
                    data: ratio[name],
                    markPoint : {
                        data : [
                            {type : 'max', name: '最大值'},
                            {type : 'min', name: '最小值'}
                        ]
                    }
                })
            }
        }

        var option = {
            backgroundColor:'#F0F0F0',
            title : {
                text: trends_title,
                x:'center',
                textStyle:{
                    fontSize: 13,
                }
            },
            tooltip : {
                trigger: 'axis'
            },
            legend: {
                    orient:'vertical',
                    x : 'left',
                    data: legend_data
            },
            toolbox: {
                show : true,
                feature : {
                    mark : {show: true},
                    dataView : {show: true, readOnly: false},
                    magicType : {show: true, type: ['line', 'bar']},
                    restore : {show: true},
                    saveAsImage : {show: true}
                }
            },
            calculable: true,
            xAxis: [
                {
                    type : 'category',
                    boundaryGap : false,
                    data : axis_time
                }
            ],
            yAxis: [
                {
                    type : 'value',
                    splitNumber: 0.7,
                    axisLabel: {
                        formatter: '{value}'
                    }
                }
            ],
            series: series_data
        };

        var myChart = echarts.init(document.getElementById(trend_div_id));
        myChart.setOption(option);

        getweibos_data();
        //pull_evolution_count(total_nodes, times_init, begin_ts, during);
    }

    var weibos_ajax_url = "/moodlens/weibos_data/?evolution=forward&query="+query+"&ts=" + end_ts;
    var weibos_ajax_method = "GET";
    var end_ts = END_TS;
    function weibos_ajax_callback(data){
        $("#vertical-ticker").empty();
        var original_length = data['forward'].length;
        if(original_length > 0){
            var weibos = [];
            for(var i = 0; i < original_length; i+=1){
                weibos.push(data['forward'][i]);
            }
            chg_weibos(weibos);
        }
        else{
            $("#vertical-ticker").empty();
            $("#vertical-ticker").append("关键微博为空！");
        }
    }

    function display_weibos(){ //请求文本数据
        $.ajax({
            url: weibos_ajax_url,
            type: weibos_ajax_method,
            dataType: "json",
            success: weibos_ajax_callback
        });
    }

    function chg_weibos(data){   //文本写入
        var html = "";
        var emotion_content = ['happy', 'angry', 'sad'];
        for(var i=0;i<data.length;i+=1){
            if (data[i]['sentiment'] == 0){
                var emotion = 'nomood'
            }
            else{
                var emotion = emotion_content[data[i]['sentiment']-1];
            }
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
        $("#vertical-ticker").append("123");
    }

*/

