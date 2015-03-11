var province_list = ["安徽", "北京", "重庆", "福建", "甘肃", "广东", "广西", "贵州", "海南", "河北", "黑龙江", "河南", "湖北", "湖南", "内蒙古", "江苏", "江西", "吉林", "辽宁", "宁夏", "青海", "山西", "山东", "上海", "四川", "天津", "西藏", "新疆", "云南", "浙江", "陕西", "台湾", "香港", "澳门"];
var topic = QUERY;
var START_TS = START_TS;
var END_TS = END_TS;
var DURING_INTERGER = POINT_INTERVAL;
function FrontPage(topic, start_ts, end_ts, pointInterval){
    this.query = topic;
    this.start_ts = start_ts;
    this.end_ts = end_ts;
    this.pointInterval = pointInterval;
    this.map_div_id = "migration";
    this.weibo_tab_id = "Tableselect_3";
    this.weibo_cont_id = "vertical-ticker_3";
    this.weibo_more_id = "more_information_3";
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
            that.showMigration();
        }
    });
}
FrontPage.prototype.addDirectionChangeListener = function(){
    var that = this;
    $("#in_list").click(function(){
        drawMigration(that,1);
    });
    $("#out_list").click(function(){
        drawMigration(that,2);
    });
}
FrontPage.prototype.whole_map_ajax_url = function(query, start_ts, end_ts, pointInterval){
    return "/evolution/in_out_map/?topic=" + query + "&start_ts=" + start_ts + "&end_ts=" + end_ts + "&pointInterval=" + pointInterval;
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
    var ajax_url = this.whole_map_ajax_url(this.query, this.start_ts, this.end_ts, this.pointInterval);
    var myMigration = echarts.init(document.getElementById(this.map_div_id));
    this.myMigration = myMigration;

    myMigration.showLoading({
        effect:'bar',
    });
    var that = this;

    if (global_data){
        myMigration.hideLoading();
        that.myData = global_data;
        drawMigration(that, 0);
    }
    else{
        this.call_async_ajax_request(ajax_url, this.ajax_method, callback);
    }
    function callback(data){
        myMigration.hideLoading();
        that.myData = data;
        global_data = data;
        top_city_weibo = data["top_city_weibo"];
        drawMigration(that, 0);
    }
}

var frontpage = new FrontPage(topic, START_TS, END_TS, POINT_INTERVAL);
var cur_city;
frontpage.addSwitchTabListener();
frontpage.addDirectionChangeListener();

function drawMigration(that, par){

    var ldata = that.myData.draw_line_data;
    var sdata = that.myData.statistics_data;
    var cdata = that.myData.in_out_results;
    if ((ldata.length < 1) || (sdata.length < 1) || (cdata.length < 1)){
        return;
    }
    var myMigration = that.myMigration;
    var lgroup = ldata[ldata.length - 1];
    var sgroup = sdata[sdata.length - 1];
    var cgroup = cdata[cdata.length - 1];

    if (par == 0){
        var option = {
            backgroundColor: '#1b1b1b',
            color: ['gold','aqua','lime'],
            title : {
                text: '微博地域迁徙图',
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
            legend: {
                orient: 'vertical',
                x:'left',
                data:[],
                selectedMode: 'single',
                selected:{},
                textStyle : {
                    color: '#fff'
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
                        optionToContent:function(v){
                            var results = '';
                            for (var i = 1;i < v.series.length; i++){
                                var sname = v.series[i]["name"];
                                var sldata = v.series[i]["markLine"]["data"];
                                // var spdata = v.series[i]["markPoint"]["data"];
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
            ]
        }
        var city_list = work_legend(cgroup, option);
        drawtab(city_list, that.weibo_tab_id, that.weibo_cont_id, that.weibo_more_id);
        work_series_data(lgroup, sgroup, option);
        myMigration.setOption(option);

        // legend event
        var ecConfig = echarts.config;
        myMigration.on(ecConfig.EVENT.LEGEND_SELECTED, function(param){
            var selected = param.selected;
            for (var key in selected){
                if (selected[key] == true){
                    cur_city = key;
                    work_out_list(cgroup, cur_city);
                    break;
                }
            }
        });

        cur_city = option.legend['data'][0];
        work_out_list(cgroup, cur_city);
    }
    else if (par == 1){
        work_in_list(cgroup, cur_city);
    }
    else if (par == 2){
        work_out_list(cgroup, cur_city);
    }
    // legend setting function
    function work_legend(cgroup, option){
        var legend_num = 5;
        for (var m=0;m < legend_num;m++){
            option.legend['data'].push(cgroup[m][0]);
            if (m == 0){
                option.legend['selected'][cgroup[m][0]] = true;
            }
            else{
                option.legend['selected'][cgroup[m][0]] = false;
            }
        }
        return option.legend['data'];
    }
    // series setting function
    function work_series_data(lgroup, sgroup, option){
        var series_gen = function(sname, data_1, data_2){
            return {
                name: sname,
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
                    data : data_1
                },
                markPoint : {
                    symbol:'emptyCircle',
                    symbolSize : function (v){
                        return 10 + v/1000
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
                    data : data_2
                }
            };
        }

        var legend_list = option.legend['data'];
        var total_list = sgroup[2];
        var max_repost = 0;

        for (var m=0;m < legend_list.length;m++){

            var sname = legend_list[m];
            var data_1 = [];
            var data_2 = [];

            for (var key in lgroup){
                var cities = key.split('-');

                if ((cities[0] in city2lnglat) && (cities[1] in city2lnglat)){

                    if ((cities[0] == sname)||(cities[1] == sname)){
                        var repost_count = lgroup[key]['count'];
                        if (repost_count > max_repost){
                            max_repost = repost_count;
                        }
                        data_1.push([{name:cities[0]},{name:cities[1], value: repost_count}]); // markLine

                        if (lgroup[key]['rank'] >= 1){
                            for (var n=0;n < total_list.length;n++){ // markPoint
                                if (total_list[n][0] == cities[0]){
                                    data_2.push({name:cities[0], value:total_list[n][1][0]});
                                    if (total_list[n][1][0] > max_repost){
                                        max_repost = total_list[n][1][0];
                                    }
                                }
                                if (total_list[n][0] == cities[1]){
                                    data_2.push({name:cities[1], value:total_list[n][1][0]});
                                    if (total_list[n][1][0] > max_repost){
                                        max_repost = total_list[n][1][0];
                                    }
                                }
                            }
                        }
                    }
                }
            }
            var series_temp = series_gen(sname, data_1, data_2);
            option.series.push(series_temp);
        }
        option.dataRange['max'] = Math.ceil(max_repost / 10) * 10;
    }
}

function work_out_list(cgroup, city){
    var cellCount = 5;
    var table = '<table class="table table-bordered">';
    var tbody = '<tbody>';
    var analy_data;

    for (var m=0;m < cgroup.length;m++){
        if (cgroup[m][0] == city){
            analy_data = cgroup[m];
            break;
        }
        if (m == cgroup.length){
            console.log('in:'+city+'not found');
            return;
        }
    }

    var length = Math.min(analy_data[1]['out'].length, TOP_LIMIT);

    for (var i = 0;i < length; i++){
        var tr = '<tr>';
        var total = analy_data[1]['out_total'];
        for(var j = 0;j < cellCount;j++){
            if(j == 0){
                var td = '<td><span class="label label-important">'+ (i+1) +'</span></td>';
            }
            else if(j == 1){
                var td = '<td>'+analy_data[0]+'</td>';
            }
            else if(j == 2){
                var td = '<td><img src="/static/mapview/images/array2.png" style="height:20px;"></td>';
            }
            else if(j == 3){
                var td = '<td>'+analy_data[1]['out'][i][0]+'</td>';
            }
            else if(j == 4){
                var td = '<td>'+Math.round(analy_data[1]['out'][i][1]*100/total)/1+'%</td>';
            }
            tr += td;
        }
        tr += '</tr>';
        tbody += tr;
    }
    tbody += '</tbody>';
    table += tbody;
    table += '</table>';

    $("#in_out_list").html(table);
}
function work_in_list(cgroup, city){
    var cellCount = 5;
    var table = '<table class="table table-bordered">';
    var tbody = '<tbody>';
    var analy_data;

    for (var m=0;m < cgroup.length;m++){
        if (cgroup[m][0] == city){
            analy_data = cgroup[m];
            break;
        }
        if (m == cgroup.length){
            console.log('in:'+city+'not found');
            return;
        }
    }

    var length = Math.min(analy_data[1]['in'].length, TOP_LIMIT);

    for (var i = 0;i < length; i++){
        var tr = '<tr>';
        var total = analy_data[1]['in_total'];
        for(var j = 0;j < cellCount;j++){
            if(j == 0){
                var td = '<td><span class="label label-important">'+ (i+1) +'</span></td>';
            }
            else if(j == 1){
                var td = '<td>'+analy_data[1]['in'][i][0]+'</td>';
            }
            else if(j == 2){
                var td = '<td><img src="/static/mapview/images/array2.png" style="height:20px;"></td>';
            }
            else if(j == 3){
                var td = '<td>'+analy_data[0]+'</td>';
            }
            else if(j == 4){
                var td = '<td>'+Math.round(analy_data[1]['in'][i][1]*100/total)/1+'%</td>';
            }
            tr += td;
        }
        tr += '</tr>';
        tbody += tr;
    }
    tbody += '</tbody>';
    table += tbody;
    table += '</table>';

    $("#in_out_list").html(table);
}


