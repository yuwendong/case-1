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

// IdentifyNews Constructor
function IdentifyNews(topic, start_ts, end_ts){
    // instance property
    this.topic = topic;
    this.start_ts = start_ts;
    this.end_ts = end_ts;

    this.news_limit_count = 10; //default number to add 
    this.news_skip = 0; //number of the news now

    this.early_adopter_div = 'firstuser_news_ul';
    this.early_adopter_rm = 'timestamp';

    this.trend_maker_div = 'trend_maker_ul';
    this.trend_maker_rm = 'weight';

    this.trend_pusher_div = 'trend_pusher_ul';
    this.trend_pusher_rm = 'comments_count';

    this.early_adopter_url = function(topic, start_ts, end_ts, early_adopter_rm){
        return '/identify/news_first_user/?topic=' + topic + '&start_ts=' + start_ts + '&end_ts=' + end_ts + '&rank_method=' + early_adopter_rm + '&news_skip=' + news_skip + '&news_limit_count=' + news_limit_count;
    }
    this.news_trend_maker_url = function(topic, start_ts, end_ts, trend_maker_rm){
        return '/identify/news_trend_maker/?topic=' + topic + '&start_ts=' + start_ts + '&end_ts=' + end_ts + '&rank_method=' + trend_maker_rm + '&news_skip=' + news_skip + '&news_limit_count=' + news_limit_count;
    }
    this.news_trend_pusher_url = function(topic, start_ts, end_ts, trend_pusher_rm){
        return '/identify/news_trend_pusher/?topic=' + topic + '&start_ts=' + start_ts + '&end_ts=' + end_ts + '&rank_method=' + trned_pusher_rm + '&news_skip=' + news_skip + '&news_limit_count=' + news_limit_count;         
    }

    this.ajax_method = 'GET';
    this.call_sync_ajax_request = function(url, method, callback){
        $ajax({
            url : url,
            type : method,
            dataType : 'json',
            async : true,
            success : callback 
        })
    }

    var that = this;

    $('#sort_by_timestamp1').click(function(){
        $('#sort_by_timestamp1').css('color', '#333');
        $('#sort_by_weight1'),css('color', '-webkit-link');

        that.news_skip = 0;
        that.early_adopter_rm = 'timestamp';
        var ajax_url = that.early_adopter_url(that.topic, that.start_ts, that.end_ts, that.early_adopter_rm, that.news_skip, that.news_limit_count);

        that.call_sync_ajax_request(ajax_url, that.ajax_method, News_function);

        function News_function(data){
            $('#' + that.early_adopter_div).empty();
            that.news_skip += that.news_limit_count;
            news_display(data, that.early_adopter_div);
        }
    });

    $('#sort_by_weight1').click(function(){
        $('#sort_by_weight1').css('color', '#333');
        $('#sort_by_timestamp1'),css('color', '-webkit-link');

        that.news_skip = 0;
        that.early_adopter_rm = 'weight';
        var ajax_url = that.early_adopter_url(that.topic, that.start_ts, that.end_ts, that.early_adopter_rm, that.news_skip, that.news_limit_count);

        that.call_sync_ajax_request(ajax_url, that.ajax_method, News_function);

        function News_function(data){
            $('#' + that.early_adopter_div).empty();
            that.news_skip += that.news_limit_count;
            news_display(data, that.early_adopter_div);
        }
    });

    $('#sort_by_timestamp2').click(function(){
        $('#sort_by_timestamp2').css('color', '#333');
        $('#sort_by_weight2'),css('color', '-webkit-link');

        that.news_skip = 0;
        that.trend_maker_rm = 'timestamp';
        var ajax_url = that.news_trend_maker_url(that.topic, that.start_ts, that.end_ts, that.trend_maker_rm, that.news_skip, that.news_limit_count);

        that.call_sync_ajax_request(ajax_url, that.ajax_method, News_function);

        function News_function(data){
            $('#' + that.trend_maker_div).empty();
            that.news_skip += that.news_limit_count;
            news_display(data, that.trend_maker_div);
        }
    });

    $('#sort_by_weight2').click(function(){
        $('#sort_by_weight2').css('color', '#333');
        $('#sort_by_timestamp2'),css('color', '-webkit-link');

        that.news_skip = 0;
        that.trend_maker_rm = 'weight';
        var ajax_url = that.news_trend_maker_url(that.topic, that.start_ts, that.end_ts, that.trend_maker_rm, that.news_skip, that.news_limit_count);

        that.call_sync_ajax_request(ajax_url, that.ajax_method, News_function);

        function News_function(data){
            $('#' + that.trend_maker_div).empty();
            that.news_skip += that.news_limit_count;
            news_display(data, that.trend_maker_div);
        }
    });

    $('#sort_by_comments_count').click(function(){
        $('#sort_by_comments_count').css('color', '#333');
        $('#sort_by_timestamp3').css('color', '-webkit-link');
        $('#sort_by_weight3').css('color', '-webkit-link');
        that.news_skip = 0;
        that.trend_pusher_rm = 'comments_count';
        var ajax_url = that.news_trend_pusher_url(that.topic, that.start_ts, that.end_ts, that.trend_pusher_rm, that.news_skip, that.news_limit_count);
        
        that.call_sync_ajax_request(ajax_url, that.ajax_method, News_function);
         
        function News_function(data){
            $('#' + that.trend_pusher_div).empty();
            that.news_skip += that.news_limit_count;
            news_display(data, that.trend_pusher_div);
        } 
    });

    $('#sort_by_timestamp3').click(function(){
        $('#sort_by_timestamp3').css('color', '#333');
        $('#sort_by_weight3'),css('color', '-webkit-link');
        $('#sort_by_comments_count').css('color', '-webkit-link');

        that.news_skip = 0;
        that.trend_pusher_rm = 'timestamp';
        var ajax_url = that.news_trend_pusher_url(that.topic, that.start_ts, that.end_ts, that.trend_pusher_rm, that.news_skip, that.news_limit_count);

        that.call_sync_ajax_request(ajax_url, that.ajax_method, News_function);

        function News_function(data){
            $('#' + that.trend_pusher_div).empty();
            that.news_skip += that.news_limit_count;
            news_display(data, that.trend_pusher_div);
        }
    });

    $('#sort_by_weight3').click(function(){
        $('#sort_by_weight3').css('color', '#333');
        $('#sort_by_timestamp3'),css('color', '-webkit-link');
        $('#sort_by_comments_count').css('color', '-webkit-link');

        that.news_skip = 0;
        that.trend_pusher_rm = 'weight';
        var ajax_url = that.news_trend_pusher_url(that.topic, that.start_ts, that.end_ts, that.trend_pusher_rm, that.news_skip, that.news_limit_count);

        that.call_sync_ajax_request(ajax_url, that.ajax_method, News_function);

        function News_function(data){
            $('#' + that.trend_pusher_div).empty();
            that.news_skip += that.news_limit_count;
            news_display(data, that.trend_pusher_div);
        }
    });

    $("#more_information1").click(function(){
        var div_id = "firstuser_news_ul";
        var ajax_url = that.early_adopter_url(that.topic, that.start_ts, that.end_ts, that.early_adopter_rm, that.news_skip, that.news_limit_count);

        that.call_sync_ajax_request(ajax_url, that.ajax_method, News_function);

        function News_function(data){
            if (data.length == 0){
                $("more_information1").html("加载完毕");
            }
            else{
                that.news_skip += that.news_limit_count;
                news_display(data, div_id);
                $('#more_information1').html("加载更多");
            }
        }

    });

    $("#more_information2").click(function(){
        var div_id = "trend_maker_ul";
        var ajax_url = that.trend_maker_ul(that.topic, that.start_ts, taht.end_ts, that.trend_maker_rm, that.news_skip, that.news_limit_count);

        that.call_sync_ajax_request(ajax_url, that.ajax_method, News_function);

        function News_function(data){
            if (data.length == 0){
                $("#more_information2").html("加载完毕");
            }
            else{
                that.news_skip += that.news_limit_count;
                news_display(data, div_id);
                $("#more_information2").html("加载更多");
            }
        }
    });

    $("#more_information3").click(function(){
        var div_id = "trend_pusher_ul";
        var ajax_url = that.trend_pusher_ul(that.topic, that.start_ts, that.end_ts, that.trend_pusher_rm, that.news_skip, that.news_limit_count);

        that.call_sync_ajax_request(ajax_url, that.ajax_method, News_function);

        function News_function(data){
            if (data.length == 0){
                $("#more_information3").html("加载完毕");
            }
            else{
                that.news_skip += that.news_limit_count;
                news_display(data, div_id);
                $("#more_information3").html("加载更多")；
            }
        }
    });

}

//instance method
IdentifyNews.prototype.pullEarlyAdopter = function(){
    var that = this;
    this.news_skip = 0;
    this.early_adopter_rm = 'timestamp';
    $('#sort_by_timestamp1').css('color', '#333');
    $('#sort_by_weight1').css('color', '-webkit-link');
    var ajax_url = this.early_adopter_url(this.topic, this.start_ts, this.end_ts, this.early_adopter_rm, this.news_skip, this.news_limit_count);
    this.call_async_ajax_request(ajax_url, this.ajax_method, early_adopter_callback)

    function early_adopter_callback(data){
        $('#' + that.early_adopter_div).empty();
        that.news_skip += that.news_limit_count;
        news_display(data, this.early_adopter_div);
    }
}

//instance method
IdentifyNews.prototype.pullNewsTrendMaker = function(){
    var that = this;
    this.news_skip = 0;
    this.trend_maker_rm = 'weight';
    $('#sort_by_weight2').css('color', '#333');
    $('#sort_by_timestamp2').css('color', '-webkit-link');
    var ajax_url = this.news_trend_maker_url(this.topic, this.start_ts, this.end_ts, this.trend_maker_rm, this.news_skip, this.news_limit_count);

    this.call_async_ajax_request(ajax_url, this.ajax_method, trend_maker_callback);

    function trend_maker_callback(data){
        $('#' + that.trend_maker_div).empty();
        that.news_skip += that.news_limit_count;
        news_display(data, this.trend_maker_div);
    }
}

// instance trend pusher
IdentifyNews.prototype.pullNewsTrendPusher = function(){
    var that = this;
    this.news_skip = 0;
    this.trend_pusher_rm = 'comments_count';
    $('#sort_by_comments_count').css('color', '#333');
    $('#sort_by_weight3').css('color', '-webkit-link');
    $('#sort_by_timestamp3').css('color', '-webkit-link');

    var ajax_url = this.news_trend_pusher_url(this.topic, this.start_ts, this.end_ts, this.trend_pusher_rm, this.news_skip, this.news_limit_count);

    this.call_async_ajax_request(ajax_url, this.ajax_method, trend_pusher_callback);

    function trend_maker_callback(data){
        $('#' + that.trend_pusher_div).empty();
        that.news_skip += that.news_limit_count;
        news_display(data, this.trend_pusher_div);
    }

}


// news display
function news_display(data, div_id){
    $('#' + div_id).empty();
    if (data == []){
        $('#' + div_id).append("<a style='font-size:1ex'>计算中...</a>");
        return;
    }
    var html = '';
    for (var i = 0; i < data.length; i += 1){
        var news_row = data[i];
        var news_id = news_row[0];
        var url = news_row[1];
        var summary = news_row[2];
        var timestamp = news_row[3];
        var datetime = news_row[4];
        var source_from_name = news_row[5];
        var content168 = news_row[6];
        var content_summary = content168.substring(0, 168) + '...';
        var title = news_row[7];
        var same_news_num = news_row[8];
        var transmit_name = news_row[9];
        var weight = news_row[10];
        
        html += '<li class="item" style="width:1010px"';
        html += '<div class="weibo_detail">';
        html += '<p>媒体:<a class="undlin" target="_blank" href="javascript;">' + source_from_name + '</a>&nbsp;&nbsp;发布:';
        html += '<span class="title" style="color:#0000FF" id="'+ div_id + '_' +news_id + '"><b>[' + title + ']</b></span>';
        html += '&nbsp;&nbsp;发布内容: &nbsp;&nbsp;<span id="content_summary_'+ div_id + '_' + news_id + '">' + content_summary + '</span>';
        html += '<span style="display: none;" id="content_' + div_id + '_' + news_id + '">' + content168 + '&nbsp;&nbsp;</span>';
        html += '</p>'
        html += '<div class="weibo_info">';
        html += '<div class="weibo_pz" style="margin-right:10px;">';
        html += '<span id="detail_"' + div_id + '_' + news_id + '><a class="undlin" href="javascript:;" target="_blank" onclick="detail_text(\'' + div_id + ',' + news_id + '\')";>阅读全文</a></span>&nbsp;&nbsp;|&nbsp;&nbsp;';
        html += '<a class="undlin" href="javascript:;" target="_blank" onclick="open_same_list(\'' + news_id + '\')";>相似新闻(' + same_news_num + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
        html += '<a href="javascript:;" target="_blank">相关度(' + weight + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
        
        if (div_id=="trend_pusher_ul"){
            var comments_count = news_row[11];
            html += '<a href="javascript:;" target="_blank">评论数(' + comments_count + ')</a>&nbsp;&nbsp;'; 
        }
        
        html += '</div>';
        html += '<div class="m">';
        html += '<a>' + new Date(timestamp * 1000).format("yyyy-MM-dd hh:mm:ss") + '</a>&nbsp;-&nbsp;';
        html += '<a>转载于' + transmit_name + '</a>&nbsp;&nbsp;';
        html += '<a target="_blank" href="' + url + '">新闻</a>&nbsp;&nbsp;';
        html += '</div>';
        html += '</div>';
        html += '</div>';
        html += '</li>';

    }
    $('#' + div_id).append(html);
    // 考虑呈现字段的选择 
    $("#content_control_height_" + div_id).css("height", $("#" + div_id).css("height"));
}

function summary_text(div_id , text_id){
    $('#content_summary_' + div_id + '_' + text_id).css("display", "inline");
    $('#content_' + div_id + '_' + text_id).css("display", "none");
    $('#detail_' + div_id + '_' + text_id).html("<a href='javascript:;' target='_blank' onclick=\"detail_text(\'" + text_id + "\');\">阅读全文</a>&nbsp;&nbsp;");
    $('#content_control_height_' + div_id).css("height", $("#" + div_id).css("height"));
}

function detail_text(div_id, text_id){
    $('#content_summary_' + div_id + '_' + text_id).css('display', 'none');
    $('#content_' + div_id + '_' + text_id).css("display", 'inline');
    $('#detail_' + div_id + '_' + text_id).html("<a href='javascript:;' target='_blank' onclick=\"summary_text(\'" + text_id + "\');\">阅读概述</a>&nbsp;&nbsp;");
    $('#content_control_height_' + div_id).css('height', $("#" + div_id).css("height"));
}


test = new IdentifyNews(QUERY, START_TS, END_TS)
test.pullEarlyAdopter();
test.pullNewsTrendMaker();
test.pullNewsTrendPusher();
