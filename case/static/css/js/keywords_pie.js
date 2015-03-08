var topic = QUERY;
if(topic == '中国'){
  var start_ts = 1377964800 + 900;
}
else{
  var start_ts = START_TS;
}
var end_ts = END_TS;

function Opinion_timeline(query, start_ts, end_ts, pointInterval){
    this.query = query;
    this.start_ts = start_ts;
    this.end_ts = end_ts;
    this.pointInterval = pointInterval; // 图上一点的时间间隔
    this.weibo_limit_count = 10; // 每次加载10条微博
    this.weibo_skip = 0; // 当前页面已显示的微博数
    this.weibo_sort = sort_weight; // 当前页面微博排序依据
    this.eventriver_ajax_url = function(query, end_ts, during){
        return "/index/eventriver/?query=" + query + "&during=" + during + "&ts=" + end_ts;
    }
    this.pie_ajax_url = function(query, end_ts, during, subevent){
        return "/news/ratio/?query=" + query + "&subevent=" + subevent + "&during=" + during + "&ts=" + end_ts;
    }
    this.cloud_ajax_url = function(query, end_ts, during, subevent){
        return "/news/keywords/?query=" + query + "&subevent=" + subevent + "&during=" + during + "&ts=" + end_ts;
    }
    this.weibo_ajax_url = function(query, end_ts, during, subevent, skip, limit, sort){
        var url = "/news/weibos/?query=" + query + "&limit=" + limit + "&skip=" + skip + "&ts=" + end_ts + "&during=" + during + "&subevent=" + subevent + "&sort=" + sort;
        return url
    }
    this.sub_weibo_ajax_url = function(query){
        return "/news/sentiment/?query=" + query;
    }
    this.subevent_pie_ajax_url =  function(query){
        return "/news/subeventpie/?query=" + query + "-微博";
    }
    this.sentiment_pie_ajax_url =  function(query){
        return "/news/sentimentpie/?query=" + query + "-微博";
    }
    this.peak_ajax_url = function(data, ts_list, during, subevent){
        return "/news/peak/?lis=" + data.join(',') + "&ts=" + ts_list + '&during=' + during + "&subevent=" + subevent;
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

    this.trend_div_id = 'trend_div';
    this.trend_title = '热度走势图';
    this.trend_chart;

    this.event_river_data; // 接收eventriver的数据
    this.select_subevent = "global"; // 当前选择的subevent, global表示总体，subeventid表示各子事件
    this.select_subevent_name = query;

    this.click_status = 'global'; // 标识当前的状态，global表示全局，peak表示点击了某个拐点后的情况
    var that = this;
    $("#clickalltime").click(function(){
        $("#cloudpie").css("display", "block");
        drawStatusTip(that.select_subevent_name, "全时段", null);
        that.drawTrendline();
        that.pullDrawPiedata();
        that.pullDrawClouddata();
        that.pullDrawWeibodata();
    });

    this.trend_count_obj = {
        "ts": [],
        "count": []
    };
}

// 绘制eventriver
Opinion_timeline.prototype.drawEventriver = function(){
    drawEventstack(this.event_river_data); // 主题河
}

// pull eventriver data
Opinion_timeline.prototype.pull_eventriver_data = function(){
    var that = this; //向下面的函数传递获取的值
    var ajax_url = this.eventriver_ajax_url(this.query, this.end_ts, this.end_ts - this.start_ts); //传入参数，获取请求的地址

    this.call_sync_ajax_request(ajax_url, this.ajax_method, Timeline_function); //发起ajax的请求

    function Timeline_function(data){    //数据的处理函数
        that.event_river_data = data;
        that.select_subevent = 'global'; // 默认处理总体
        subevent_list = data['eventList'];
    }
}

Opinion_timeline.prototype.drawFishbone = function(){
    drawFishbone(this.event_river_data);
}

function timestamp_comparator(a, b){
    return parseInt(a.news.timestamp) - parseInt(b.news.timestamp);
}

// 绘制鱼骨图
function drawFishbone(data){
    var html = '';
    data['eventList'].sort(timestamp_comparator);
    var eventListdata = data['eventList'];
    $(function(){
        $('#timeline1').b1njTimeline({
            'height' : eventListdata.length / 2 * 114
        });
    });

    for (var i=0; i < eventListdata.length; i++){
        var keyword = eventListdata[i]['name'];
        var news = eventListdata[i]['news'];
        var summary = news['content168'].substring(0, 100) + '...';;
        var datetime = news['datetime'];
        var title = news['title'];
        var source = news['transmit_name'];
        html += "<li><time idx='" + i + "' " + "datetime='" + datetime + "'>" + datetime +"&nbsp;&nbsp;<span>"+keyword+"</span></time>";
        html += "<p><b>【" + title + "】:</b>" + summary + "</p>";
        html += "<span>转载于"+ source + "</span>&nbsp;&nbsp;<a target=\"_blank\" href=\"" + news["url"] + "\">新闻</a></li>";
    }

    $("#timeline1").append(html);
    $("#page").css("height", eventListdata.length / 2 * 114 + 150);
}

function drawEventstack(data){
    var x_data = data['dates'];
    var data = data['eventList'];
    var series_data = [];
    var series_name = [];
    var One_series_data = {};
    var temp_data = [];
    for (var k= 0; k < data.length; k++){
        One_series_value = [];
        One_series_time = [];
        temp_data = [];
        for(var i = 0; i < data[k]['evolution'].length; i++){
            One_series_value.push(data[k]['evolution'][i]['value']);
            temp_data.push(data[k]['evolution'][i]['value']);
            One_series_time.push(data[k]['evolution'][i]['time']);
        }
        if(One_series_value.length < x_data.length){
            for(var j = 0; j < x_data.length; j++){
                One_series_value[j] = 0;
                for(var m = 0; m < One_series_time.length; m++){
                    if(x_data[j] == One_series_time[m]){
                        One_series_value[j] = temp_data[m];
                    }
                }
            }
        }

        One_series_data = {'name':data[k]['name'], 'type':'line', 'smooth':true,'itemStyle':{'normal': {'areaStyle': {'type': 'default'}}},  'data':One_series_value};
        series_name.push(One_series_data['name']);
        series_data.push(One_series_data);
    }

    var selected_series_count = 10;
    if(selected_series_count > series_name.length){
        selected_series_count = series_name.length;
    }
    var selected_series_dict = {};
    for(var i = selected_series_count; i < series_name.length; i++){
        selected_series_dict[series_name[i]] = false;
    }

    var option = {
        tooltip : {
            trigger: 'axis'
        },
        legend: {
            data: series_name, 
            selected: selected_series_dict,
            selectedMode : "multiple"
        },
        calculable : true,
        xAxis : [
            {type : 'category',
            boundaryGap : false,
            data : x_data
            }
        ],
        yAxis : [
            {type : 'value'}
        ],
        series : series_data
    };
    var myChart = echarts.init(document.getElementById('event_river'));
    myChart.setOption(option); 
}

var query = QUERY;
var start_ts = START_TS;
var end_ts = END_TS;
var pointInterval = 3600 * 24;
var global_sub_weibos;
var sort_weight = "weight";
var opinion = new Opinion_timeline(query, start_ts, end_ts, pointInterval);
opinion.pull_eventriver_data();
opinion.drawEventriver();
opinion.drawFishbone();
