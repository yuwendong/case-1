var province_list = ["安徽", "北京", "重庆", "福建", "甘肃", "广东", "广西", "贵州", "海南", "河北", "黑龙江", "河南", "湖北", "湖南", "内蒙古", "江苏", "江西", "吉林", "辽宁", "宁夏", "青海", "山西", "山东", "上海", "四川", "天津", "西藏", "新疆", "云南", "浙江", "陕西", "台湾", "香港", "澳门"];
function FrontPage(){
    this.query = '东盟,博览会';
    this.map_div_id = "migration";
    this.ajax_method = "GET";
    this.myMigration;
    this.myData;
}
FrontPage.prototype.addSwitchTabListener=function(){
    var that = this;
    var select_a;
    var unselect_a;
    $("#mapTabDiv").children("[status='front']").click(function(){
        select_a = $(this);
        unselect_a = $(this).siblings('a');
        if(!select_a.hasClass('curr')) {
            select_a.addClass('curr');
            unselect_a.removeClass('curr');
        }
        that.showMigration();
    });
}
/* FrontPage.prototype.addPageListener=function(){
    $('#rank_page_selection').bootpag({
        total: 10,
        page: 1,
        // maxVisible: 30
    }).on("page", function(event, num){
        current_num = num;
        start_row = (num - 1)* page_num;
        end_row = start_row + page_num;
        if (end_row > current_data.length)
        end_row = current_data.length;
        show_weibo();
    });
}
*/
FrontPage.prototype.whole_map_ajax_url = function(query){
    return "/evolution/city_map_view/";
}
FrontPage.prototype.call_sync_ajax_request = function(url, method, callback){
    $.ajax({
        url: url,
        type: method,
        dataType: "json",
        async: false,
        success: callback
    })
}
FrontPage.prototype.call_async_ajax_request = function(url, method, callback){
    $.ajax({
        url: url,
        type: method,
        dataType: "json",
        async: true,
        success: callback
    })
}
FrontPage.prototype.disposeMyMigration = function(){
    if (this.myMigration){
        this.myMigration.dispose();
        this.myMigration = false;
    }
}
FrontPage.prototype.showMigration = function(){
    this.disposeMyMigration();
    this.initPullDrawMigration();
}
FrontPage.prototype.initPullDrawMigration = function(){
    var ajax_url = this.whole_map_ajax_url(this.query);
    var myMigration = echarts.init(document.getElementById(this.map_div_id));
    this.myMigration = myMigration;

    myMigration.showLoading({
        text: '努力加载数据中...',
    });
    var that = this;
    this.call_async_ajax_request(ajax_url, this.ajax_method, callback);

    function callback(data){
        myMigration.hideLoading();
        that.myData = data;
        drawMigration(that);
    }
}

var frontpage = new FrontPage();
// var current_num = 1;
// var current_city;
frontpage.addSwitchTabListener();

function drawWholeBaiduMap(that, par){
    var myMap = that.myMap;
    var ldata = that.myData.draw_line_data;
    var sdata = that.myData.statistics_data;
    var index = ldata.length - 1;

    var lgroup = ldata[index];
    var sgroup = sdata[index];
    if (par == 0){
        work_map(lgroup, sgroup, myMap);
        work_list(sgroup, myMap);
    }
    else if(par == 1){
        work_list(sgroup, myMap);
    }
}

function drawMigration(that){

    var option = {
        backgroundColor: '#1b1b1b',
        color: ['gold','aqua','lime'],
        title : {
            text: '模拟迁徙',
            // subtext:'数据纯属虚构',
            x:'center',
            textStyle : {
                color: '#fff'
            }
        },
        tooltip : {
            trigger: 'item',
            formatter: function (v) {
                return v[1].replace(':', ' > ');
            }
        },
        /*
        legend: {
            orient: 'vertical',
            x:'left',
            data:['北京 Top10', '上海 Top10', '广州 Top10'],
            selectedMode: 'single',
            selected:{
                '上海 Top10' : false,
                '广州 Top10' : false
            },
            textStyle : {
                color: '#fff'
            }
        },
        */
        toolbox: {
            show : true,
            orient : 'vertical',
            x: 'right',
            y: 'center',
            feature : {
                mark : {show: true},
                dataView : {show: true, readOnly: false},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        dataRange: {
            min : 0,
            max : 100,
            calculable : true,
            color: ['#ff3333', 'orange', 'yellow','lime','aqua'],
            textStyle:{
                color:'#fff'
            }
        },
        series : [
            {
                name: '全国',
                type: 'map',
                // roam: true,
                hoverable: false,
                mapType: 'china',
                itemStyle:{
                    normal:{
                        borderColor:'rgba(100,149,237,1)',
                        borderWidth:0.5,
                        areaStyle:{
                            color: '#1b1b1b'
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
                name: '北京 Top10',
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
                        return 10 + v/10
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
    var ldata = that.myData.draw_line_data;
    var sdata = that.myData.statistics_data;
    var myMigration = that.myMigration;
    var lgroup = ldata[ldata.length - 1];
    var sgroup = sdata[sdata.length - 1];
    var total_list = sgroup[2];
    var cities;
    var max_repost = 0;
    var data_1 = [];
    var data_2 = [];
    var data_3 = [];

    for (var key in lgroup){
        cities = key.split('-');
        if ((cities[0] in city2lnglat) && (cities[1] in city2lnglat)){
            var repost_count = lgroup[key]['count'];
            if (repost_count > max_repost){
                max_repost = repost_count;
            }
            if (lgroup[key]['rank'] == 1){
                data_1.push([{name:cities[0]},{name:cities[1]}]);
            }
            else if (lgroup[key]['rank'] != 1){
                data_2.push([{name:cities[0]},{name:cities[1], value: repost_count}]);
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
        option.series[0]['markLine']['data'] = data_1;
        option.series[1]['markLine']['data'] = data_2;
        option.series[1]['markPoint']['data'] = data_3;
    }
    myMigration.setOption(option);
}


function drawtab(curr_data,rank_city){
    var flag = 0;
    var html = '';
    $("#Tableselect").empty();
    for(var m = 0; m < rank_city.length; m++){
        if(flag == 0){
            html += '<a topic='+ rank_city[m] + ' ' +'class=\"tabLi gColor0 curr\" href="javascript:;" style="display: block;">';
            html += '<div class="nmTab">'+rank_city[m]+ '</div>';
            html += '<div class="hvTab">'+rank_city[m]+'</div></a>';
            show_weibo(rank_city[m], curr_data);
        }
        else{
            html += '<a topic='+rank_city[m] + ' class="tabLi gColor0" href="javascript:;" style="display: block;">';
            html += '<div class="nmTab">'+ rank_city[m] + '</div>';
            html += '<div class="hvTab">'+ rank_city[m] +'</div></a>';
        }
        flag++;
    }
    $("#Tableselect").append(html);
    bindTabClick(rank_city, curr_data);
}
function bindTabClick(rank_city, curr_data){
    $("#Tablebselect").children("a").unbind();
    $("#Tableselect").children("a").click(function() {        
        var select_a = $(this);
        var unselect_a = $(this).siblings('a');
        if(!select_a.hasClass('curr')) {
            select_a.addClass('curr');
            unselect_a.removeClass('curr');
            current_city = select_a.attr('topic');
            show_weibo(current_city, curr_data);
        }
    });
}

function show_weibo(current_city, curr_data){
    $("#vertical-ticker").empty();
    var html = '';
    var child_topic = current_city;
    var weibo_num = 10;
    var weibo_data = curr_data[child_topic];
    html += '<div class="tang-scrollpanel-wrapper" style="height: ' + 70 * weibo_num  + 'px;">';
    html += '<div class="tang-scrollpanel-content">';
    html += '<ul id="weibo_ul">';

    for(var i = 0; i < weibo_num; i += 1){
        var da = weibo_data[i];
        // var name;
        // if ('name' in da){
        //     name = da['name'];
        //     if(name == 'unknown'){
        //         name = '未知';
        //     }
        // }
        // else{
        //     name = '未知';
        // }
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
    $("#vertical-ticker").append(html);
}
