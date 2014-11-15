var province_list = ["安徽", "北京", "重庆", "福建", "甘肃", "广东", "广西", "贵州", "海南", "河北", "黑龙江", "河南", "湖北", "湖南", "内蒙古", "江苏", "江西", "吉林", "辽宁", "宁夏", "青海", "山西", "山东", "上海", "四川", "天津", "西藏", "新疆", "云南", "浙江", "陕西", "台湾", "香港", "澳门"];
var top_city_weibo;
var global_data;
// var total_city_list;
var topic = QUERY;
var START_TS = START_TS;
var END_TS = END_TS;
var DURING_INTERGER = POINT_INTERVAL;

function MapView(topic, start_ts, end_ts, pointInterval){
    this.query = topic;
    this.start_ts = start_ts;
    this.end_ts = end_ts;
    this.pointInterval = pointInterval;
    this.map_div_id = "allmap";
    this.weibo_tab_id = "Tableselect_1";
    this.weibo_cont_id = "vertical-ticker_1";
    this.weibo_more_id = "more_information_1";
    this.ajax_method = "GET";
    this.myMap;
    this.myData;

}
MapView.prototype.addSortChangeListener = function(){
    var that = this;
    $("#total_post").click(function(){
        type = 2;
        drawWholeBaiduMap(that, 1);
    });
    $("#origin").click(function(){
        type = 1;
        drawWholeBaiduMap(that, 1);
    });
    $("#repost").click(function(){
        type = 0;
        drawWholeBaiduMap(that, 1);
    });
    $("#influence").click(function(){
        type = 3;
        drawWholeBaiduMap(that, 1);
    });

}
MapView.prototype.addSwitchTabListener = function(){
    var that = this;
    var select_a;
    var unselect_a;
    $("#mapTabDiv").children("[status='end']").click(function(){
        select_a = $(this);
        unselect_a = $(this).siblings('a');
        if(!select_a.hasClass('curr')) {
            select_a.addClass('curr');
            unselect_a.removeClass('curr');
            that.showWholeMap();
        }
    });
}
MapView.prototype.whole_map_ajax_url = function(query, start_ts, end_ts, pointInterval){
    return "/evolution/city_map_view/?topic=" + query + "&start_ts=" + start_ts + "&end_ts=" + end_ts + "&pointInterval=" + pointInterval;
}
MapView.prototype.call_sync_ajax_request = function(url, method, callback){
    $.ajax({
        url: url,
        type: method,
        dataType: "json",
        async: false,
        success: callback
    })
}
MapView.prototype.call_async_ajax_request = function(url, method, callback){
    $.ajax({
        url: url,
        type: method,
        dataType: "json",
        async: true,
        success: callback
    })
}
MapView.prototype.disposeMyMap = function(){
    if (this.myMap){
        this.myMap.dispose();
        this.myMap = false;
    }
}
MapView.prototype.showWholeMap = function(){
    this.disposeMyMap();
    this.initPullDrawMap();
}
MapView.prototype.initPullDrawMap = function(){
    var ajax_url = this.whole_map_ajax_url(this.query, this.start_ts, this.end_ts, this.pointInterval);
    var myMap = echarts.init(document.getElementById(this.map_div_id));
    this.myMap = myMap;

    myMap.showLoading({
        effect:'bar'
    });
    var that = this;

    if (global_data){
        myMap.hideLoading();
        that.myData = global_data;
        drawWholeBaiduMap(that, 0);
    }
    else{
        this.call_async_ajax_request(ajax_url, this.ajax_method, callback);
    }
    function callback(data){
        myMap.hideLoading();
        that.myData = data;
        global_data = data; //全局
        top_city_weibo = data["top_city_weibo"]; //全局
        drawWholeBaiduMap(that, 0);
    }
}
var mapview = new MapView(topic, START_TS, END_TS, POINT_INTERVAL);
var type = 2; //repost-0, origin-1, post-2, influence-3
mapview.showWholeMap();
mapview.addSwitchTabListener();
mapview.addSortChangeListener();

function drawWholeBaiduMap(that, par){
    var ldata = that.myData.draw_line_data;
    var sdata = that.myData.statistics_data;
    var myMap = that.myMap;
    var lgroup = ldata[ldata.length - 1];
    var sgroup = sdata[sdata.length - 1];

    if (par == 1){
        var city_list = work_list(sgroup);
        drawtab(city_list, that.weibo_tab_id, that.weibo_cont_id, that.weibo_more_id);
    }
    else if(par == 0){
        var total_city_list = work_list(sgroup);
        drawtab(total_city_list, that.weibo_tab_id, that.weibo_cont_id, that.weibo_more_id);
        var total_list = sgroup[2];
        var cities;
        var max_repost = 0;
        var data_2 = [];
        var data_3 = [];

        var option = {
            backgroundColor: 'rgb(255,255,255)',
            color: ['gold','aqua','lime'],
            title : {
                text: '微博迁徙概况',
                // subtext:'数据纯属虚构',
                x:'center',
                textStyle : {
                    color: '#1b1b1b'
                }
            },
            tooltip : {
                trigger: 'item',
                formatter: function (v) {
                    return v[1].replace(':', ' > ');
                }
            },
            toolbox: {
                show : true,
                orient : 'vertical',
                x: 'right',
                y: 'center',
                feature : {
                    mark : {show: true},
                    dataView : {show: true,
                        readOnly: false,
                        optionToContent:function (v){
                            var results = '';
                            for (var i = 1;i < v.series.length; i++){
                                var sname = v.series[i]["name"];
                                var sldata = v.series[i]["markLine"]["data"];
                                var spdata = v.series[i]["markPoint"]["data"];
                                var sdata2str = '';
                                for (var m = 0;m < sldata.length; m++){
                                    sdata2str += sldata[m][0]["name"]+ "--" + sldata[m][1]["name"] + ":" + sldata[m][1]["value"] +";";
                                }
                                /*
                                sdata2str += '\n';
                                for (var m = 0;m < spdata.length; m++){
                                    sdata2str += spdata[m]["name"] + ':' + spdata[m]["value"] + ";";
                                }
                                */
                                results += sname + '\n' + sdata2str + '\n';
                            }
                            return results;
                        }
                    },
                    restore : {show: true},
                    saveAsImage : {show: true}
                }
            },
            dataRange: {
                min : 0,
                max : 3000,
                calculable : true,
                color: ['#ff3333', 'orange', 'yellow','lime','aqua'],
                textStyle:{
                    color:'#000000'
                }
            },
            series : [
                {
                    name: '空',
                    type: 'map',
                    // roam: true,
                    hoverable: false,
                    mapType: 'china',
                    itemStyle:{
                        normal:{
                            borderColor:'rgba(100,149,237,1)',
                            borderWidth:0.5,
                            areaStyle:{
                                color: 'rgba(254,230,121,1)'
                            }
                        }
                    },
                    data:[],
                    markLine : {
                        smooth:true,
                        symbol: ['none', 'circle'],
                        symbolSize : 1,
                        itemStyle : {
                            normal: {
                                color:'#fff',
                                borderWidth:1,
                                borderColor:'rgba(30,144,255,0.5)'
                            }
                        },
                        data : [],
                    },
                    geoCoord: city2lnglat
                },
                {
                    name: '全国',
                    type: 'map',
                    mapType: 'china',
                    data:[],
                    markLine : {
                        smooth:true,
                        effect : {
                            show: true,
                            scaleSize: 1,
                            period: 30,
                        color: '#fff',
                        shadowBlur: 10
                        },
                        itemStyle : {
                            normal: {
                                borderWidth:1,
                                lineStyle: {
                                    type: 'solid',
                                    shadowBlur: 10
                                }
                            }
                        },
                        data : []
                    },
                    markPoint : {
                        symbol:'emptyCircle',
                        symbolSize : function (v){
                            return 10 + v/100
                        },
                        effect : {
                            show: true,
                            shadowBlur : 0
                        },
                        itemStyle:{
                            normal:{
                                label:{show:false}
                            }
                        },
                        data : []
                    }
                }
            ]
        }
        for (var key in lgroup){
            cities = key.split('-');
            if ((cities[0] in city2lnglat) && (cities[1] in city2lnglat)){
                var repost_count = lgroup[key]['count'];
                if (repost_count > max_repost){
                    max_repost = repost_count;
                }
                data_2.push([{name:cities[0]},{name:cities[1], value: repost_count}]);
                if (lgroup[key]['rank'] != 1){
                    for (var m=0;m < total_list.length;m++){
                        if (total_list[m][0] == cities[0]){
                            data_3.push({name:cities[0], value:total_list[m][1][0]});
                            if (total_list[m][1][0] > max_repost){
                                max_repost = total_list[m][1][0];
                            }
                        }
                        if (total_list[m][0] == cities[1]){
                            data_3.push({name:cities[1], value:total_list[m][1][0]});
                            if (total_list[m][1][0] > max_repost){
                                max_repost = total_list[m][1][0];
                            }
                        }
                    }
                }
            }
            option.dataRange['max'] = Math.ceil(max_repost / 10) * 10;
            option.series[1]['markLine']['data'] = data_2;
            option.series[1]['markPoint']['data'] = data_3;
        }
        myMap.setOption(option);
    }

}
function work_list(sgroup){

    var cellCount = 6;
    var topLimit = 10;
    var city_list = [];
    var table = '<table class="table table-bordered">';
    var thead = '<thead><tr><th>排名</th><th>省份</th><th>微博总量</th><th>原创微博</th><th>转发微博</th><th>综合影响力</th></tr></thead>';
    var tbody = '<tbody>';

    var curData = sgroup[type];
    var type_num = sgroup.length

    for (var i = 0;i < topLimit; i++){
        var tr = '<tr>';
        var show_data = [];
        for (var v=0;v < type_num;v++){
            if (v != type){
                for (var m=0;m < sgroup[v].length; m++){
                    if (sgroup[v][m][0] == curData[i][0]){
                        show_data[v] = sgroup[v][m][1][0];
                        show_data[v+type_num] = sgroup[v][m][1][1];
                        break;
                    }
                }
                if (!show_data[v]){
                    show_data[v] = 0;
                    show_data[v+type_num] = 0;
                }
            }
            else{
                show_data[v] = curData[i][1][0];
                show_data[v+type_num] = curData[i][1][1];
            }
        }
        for(var j = 0;j < cellCount;j++){
            if(j == 0){
                var td = '<td><span class="label label-important">'+ (i+1) +'</span></td>';
            }
            else if(j == 1){
                var td = '<td>'+curData[i][0]+'</td>';
            }
            else if(j == 2){
                var td = '<td>'+show_data[2]+'</td>';
            }
            else if(j == 3){
                var td = '<td>'+show_data[1]+'</td>';
            }
            else if(j == 4){
                var td = '<td>'+show_data[0]+'</td>';
            }
            else if(j == 5){
                var td = '<td>'+show_data[3]+'</td>';
            }
            tr += td;
        }
        tr += '</tr>';
        tbody += tr;
        city_list.push(curData[i][0]);
    }
    tbody += '</tbody>';
    table += thead + tbody;
    table += '</table>';

    $("#rank_table").html(table);
    return city_list;
}

function drawtab(rank_city, weibo_tab_id, weibo_cont_id, weibo_more_id){
    var flag = 0;
    var html = '';
    var weibo_num = 10;
    $("#"+weibo_tab_id).empty();
    for(var m = 0; m < rank_city.length; m++){
        if(flag == 0){
            html += '<a topic='+ rank_city[m] + ' ' +'class=\"tabLi gColor0 curr\" href="javascript:;" style="display: block;">';
            html += '<div class="nmTab">'+rank_city[m]+ '</div>';
            html += '<div class="hvTab">'+rank_city[m]+'</div></a>';
            show_weibo(rank_city[m], weibo_tab_id, weibo_cont_id, weibo_num, weibo_more_id);
        }
        else{
            html += '<a topic='+rank_city[m] + ' class="tabLi gColor0" href="javascript:;" style="display: block;">';
            html += '<div class="nmTab">'+ rank_city[m] + '</div>';
            html += '<div class="hvTab">'+ rank_city[m] +'</div></a>';
        }
        flag ++;
    }
    $("#"+weibo_tab_id).append(html);
    bindTabClick(weibo_tab_id, weibo_cont_id, weibo_more_id);
}
function bindTabClick(weibo_tab_id, weibo_cont_id, weibo_more_id){
    var weibo_num = 10;
    $("#"+weibo_tab_id).children("a").unbind();
    $("#"+weibo_tab_id).children("a").click(function(){
        var select_a = $(this);
        var unselect_a = $(this).siblings('a');
        if(!select_a.hasClass('curr')) {
            select_a.addClass('curr');
            unselect_a.removeClass('curr');
            current_city = select_a.attr('topic');
            show_weibo(current_city, weibo_tab_id, weibo_cont_id, weibo_num, weibo_more_id);
        }
    });
}

function bindmore_weibo(weibo_num, weibo_tab_id, weibo_cont_id, weibo_more_id){
    $("#"+weibo_more_id).unbind();

    $("#"+weibo_more_id).click(function(){
        weibo_num = weibo_num + 10;
        var current_city;
        $("#"+weibo_tab_id).children("a").each(function(){
            var select_a = $(this);
            if (select_a.hasClass('curr')){
                current_city = select_a.attr('topic');
                show_weibo(current_city, weibo_tab_id, weibo_cont_id, weibo_num, weibo_more_id);
                return false;
            }
        });
    });
}

function show_weibo(current_city, weibo_tab_id, weibo_cont_id, weibo_num, weibo_more_id){
    $("#"+weibo_cont_id).empty();
    // console.log('empty');

    if ($("#"+weibo_more_id).hasClass("more_display")){
        $("#"+weibo_more_id).html('').removeClass("more_display");
        // console.log('remove');
    }

    var html = '';
    var weibo_data = top_city_weibo[current_city];
    if (weibo_data.length <= weibo_num){
        weibo_num = weibo_data.length;
    }
    else{
        var more_html = '加载更多&gt;&gt;';
        $("#"+weibo_more_id).html(more_html).addClass("more_display");
        bindmore_weibo(weibo_num, weibo_tab_id, weibo_cont_id, weibo_more_id);
        // console.log('append');
    }

    html += '<div class="tang-scrollpanel-wrapper" style="height: ' + 71 * weibo_num  + 'px;">';
    html += '<div class="tang-scrollpanel-content">';
    html += '<ul id="weibo_ul">';

    for(var i = 0; i < weibo_num; i++){
        var da = weibo_data[i];
        var text = da['text'];
        var user = da['user'];
        var name = da['username'];
        var _id = da['_id'];
        var reposts_count = da['reposts_count'];
        var comments_count = da['comments_count'];
        var timestamp = da['timestamp'];
        var data = new Date(timestamp * 1000).format("yyyy年MM月dd日 hh:mm:ss");
        var user_link = 'http://weibo.com/u/' + user;
        var user_image_link = da['bmiddle_pic'];
        var ip = da['geo'];
        var weibo_link = da['weibo_link'];
        
        html += '<li class="item"><div class="weibo_face"><a target="_blank" href="' + user_link + '">';
        html += '<img src="' + user_image_link + '">';
        html += '</a></div>';
        html += '<div class="weibo_detail">';
        html += '<p>昵称:<a class="undlin" target="_blank" href="' + user_link  + '">' + name + '</a>&nbsp;&nbsp;UID:&nbsp;&nbsp;'  + user + '&nbsp;&nbsp;于' + ip +'发布&nbsp;&nbsp;' + text + '</p>';
        html += '<div class="weibo_info">';
        html += '<div class="weibo_pz">';
        html += '<a class="undlin" href="javascript:;" target="_blank">转发(' + reposts_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
        html += '<a class="undlin" href="javascript:;" target="_blank">评论(' + comments_count + ')</a></div>';
        html += '<div class="m">';
        html += '<a class="undlin" target="_blank" href="' + weibo_link + '">' + data + '</a>&nbsp;-&nbsp;';
        html += '<a target="_blank" href="http://weibo.com">新浪微博</a>&nbsp;-&nbsp;';
        html += '<a target="_blank" href="' + user_link + '">用户页面</a>&nbsp;-&nbsp;';
        html += '<a target="_blank" href="' + weibo_link + '">微博页面</a>&nbsp;&nbsp;';
        html += '</div>';
        html += '</div>';
        html += '</div>';
        html += '</li>';
    }
    html += '</ul>';
    html += '</div>';
    $("#"+weibo_cont_id).append(html);
}
