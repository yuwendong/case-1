var province_list = ["安徽", "北京", "重庆", "福建", "甘肃", "广东", "广西", "贵州", "海南", "河北", "黑龙江", "河南", "湖北", "湖南", "内蒙古", "江苏", "江西", "吉林", "辽宁", "宁夏", "青海", "山西", "山东", "上海", "四川", "天津", "西藏", "新疆", "云南", "浙江", "陕西", "台湾", "香港", "澳门"];
/*function getLngLat(province_list){
    var num = 0;
    var myGeo = new BMap.Geocoder();
    var adds = province_list;
    bdGEO();

    function bdGEO(){
        var add = adds[num];
        geocodeSearch(add);
        num++;
    }
    function geocodeSearch(add){
        if (num < adds.length){
            setTimeout(bdGEO,400);
        }
        myGeo.getPoint(add, function(point){
            if (point){
                console.log(num +"、" + add + ":" + point.lng + "," + point.lat);
            }
        });
    }
}*/

function MapView(){
    this.query = '东盟,博览会';
    this.map_div_id = "allmap";
    this.ajax_method = "GET";
    this.myMap;

}
MapView.prototype.disposeMyMap = function(){
    if (this.myMap){
        this.myMap.reset();
    }
}
MapView.prototype.whole_map_ajax_url = function(query){
    return "/evolution/city_map_view/";
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
MapView.prototype.initMap = function(){
    this.myMap.centerAndZoom(new BMap.Point(116.404,39.915),5);
    this.myMap.setMapStyle({style: "normal"});
    this.myMap.addControl(new BMap.MapTypeControl());
    this.myMap.addControl(new BMap.NavigationControl());
    this.myMap.addControl(new BMap.ScaleControl());
    this.myMap.setCurrentCity("北京");
    // this.myMap.enableScrollWheelZoom();
}
MapView.prototype.initPullDrawMap = function(){
    var ajax_url = this.whole_map_ajax_url(this.query);
    var myMap = new BMap.Map(document.getElementById(this.map_div_id));
    this.myMap = myMap;
    this.initMap();

    /*
    $('#play_pause1').button({icons: {primary: "ui-icon-play"},text: false});
    $('#play_pause2').button({icons: {primary: "ui-icon-pause"},text: false});
    $('#play_pause3').button({icons: {primary: "ui-icon-bullet"},text: false});

    $('#play_pause1').button("option", "disabled", false);
    $('#play_pause2').button("option", "disabled", true);
    $('#play_pause3').button("option", "disabled", true);

    $("#mapContainer").blockUI({
        message: '<h2><img src="/static/mapview/images/ajax_loader.gif" />数据加载中,请稍候...</h2>'
    });
    */

    var that = this;
    this.call_async_ajax_request(ajax_url, this.ajax_method, callback);

    function callback(data){
        that.myData = data;
        console.log('ready');
        drawWholeBaiduMap(that, 0);
    }
}
MapView.prototype.showWholeMap = function(){
    this.disposeMyMap();
    this.initPullDrawMap();
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
            // stoped = true;
        }
    });
}
/*
MapView.prototype.addPauseButtonListener = function(){
    var that = this;
    $("#play_pause1").click(function(){
        if (stoped == true){
            stoped = false;
            drawWholeBaiduMap(that);
        }
    });
    $("#play_pause2").click(function(){
        if (stoped == false){
            stoped = true;
        }
    });
    $("#play_pause3").click(function(){
        index = 0;
        stoped = false;
        drawWholeBaiduMap(that);
    });
}
*/

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

function work_map(lgroup, sgroup, myMap){
    myMap.clearOverlays();
    var markers_cluster = [];
    var total = sgroup[2];
    var city;
    for (var m=0;m < total.length;m++){
        city = total[m][0];
        if (city in city2lnglat) {
            var pt_lng = city2lnglat[city][0];
            var pt_lat = city2lnglat[city][1];
            var pt = new BMap.Point(pt_lng, pt_lat);
            for (var i = 0; i < total[m][1][0]; i++){
                markers_cluster.push(new BMap.Marker(pt));
            }
        }
    }
    var markerClusterer = new BMapLib.MarkerClusterer(myMap, {markers: markers_cluster});
    var lineClusterer = new LineClusterer(myMap, lgroup);
    /*
    var cities = [];
    var markers = [];

    for (var key in lgroup){
        cities = key.split('-');
        if ((cities[0] in city2lnglat) && (cities[1] in city2lnglat) && (lgroup[key]["rank"] >= 1)){
            var begin_lng = city2lnglat[cities[0]][0];
            var begin_lat = city2lnglat[cities[0]][1];
            var end_lng = city2lnglat[cities[1]][0];
            var end_lat = city2lnglat[cities[1]][1];

            var origin_point = new BMap.Point(begin_lng, begin_lat);
            var repost_point = new BMap.Point(end_lng, end_lat);

            for (var i = 0; i < lgroup[key]["count"]; i++){
                markers.push(new BMap.Marker(origin_point));
                markers.push(new BMap.Marker(repost_point));
            }
        }
    }
    var markerClusterer = new BMapLib.MarkerClusterer(myMap, {markers: markers});
    */
}

function work_mark(sgroup, myMap){
    var repost = sgroup[0];
    var origin = sgroup[1];
    var repost_icon = new BMap.Icon("/static/mapview/images/markers/repost/3.png", new BMap.Size(30,30));
    var origin_icon = new BMap.Icon("/static/mapview/images/markers/fipost/3.png", new BMap.Size(30,30));
    var equal_icon = new BMap.Icon("/static/mapview/images/markers/equalpost/3.png", new BMap.Size(30,30));

    var city = origin[0][0];
    console.log(city);
    var origin_num =origin[0][1][0];
    if (city in city2lnglat) {
        var pt_lng = city2lnglat[city][0];
        var pt_lat = city2lnglat[city][1];
        var pt = new BMap.Point(pt_lng, pt_lat);
        // var show_string = '原创:' + origin_num + '\n转发:' + repost_num
        var show_string = 'origin';
        var marker = new BMap.Marker(pt,{icon:origin_icon, title:show_string, offset:new BMap.Size(0,-30)});

        myMap.addOverlay(marker);
    }
    /*
    for (var m=0;m < origin.length;m++){
        var origin_num = origin[m][1][0];
        city = origin[m][0];
        if (city in city2lnglat) {
            var pt_lng = city2lnglat[city][0];
            var pt_lat = city2lnglat[city][1];
            var pt = new BMap.Point(pt_lng, pt_lat);
            for (var n=0;n < repost.length;n++){
                if (repost[n][0] == city){
                    var repost_num = repost[n][1][0];
                    var result = repost_num - origin_num;
                    var marker;
                    var show_string = '原创:' + origin_num + '\n转发:' + repost_num

                    if (result > 0){
                        marker = new BMap.Marker(pt,{icon:repost_icon, title:show_string});
                    }
                    else if (result < 0){
                        marker = new BMap.Marker(pt,{icon:origin_icon, title:show_string});
                    }
                    else{
                        marker = new BMap.Marker(pt,{icon:equal_icon, title:show_string});
                    }
                    myMap.addOverlay(marker);
                    break;
                }
            }
        }
    }
    */
}

function work_list(sgroup, myMap){
    work_mark(sgroup, myMap);
    var cellCount = 7;
    var topLimit = 10;
    var table = '<table class="table table-bordered">';
    var thead = '<thead><tr><th>排名</th><th>省份</th><th>微博总量</th><th>原创微博</th><th>转发微博</th><th>综合影响力</th><th>综合影响力变化</th></tr></thead>';
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
                // rank status
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
            else{
                var td = '<td>'+show_data[3+type_num]+'</td>';
            }
            tr += td;
        }
        tr += '</tr>';
        tbody += tr;
    }
    tbody += '</tbody>';
    table += thead + tbody;
    table += '</table>';

    $("#rank_table").html(table);
}

function drawWholeBaiduMap(that, par){
    var myMap = that.myMap;
    var ldata = that.myData.draw_line_data;
    var sdata = that.myData.statistics_data;
    var index = ldata.length - 2;
    //  pointChange();

    var lgroup = ldata[index];
    var sgroup = sdata[index];
    if (par == 0){
        work_map(lgroup, sgroup, myMap);
        work_list(sgroup, myMap);
    }
    else if(par == 1){
        work_list(sgroup, myMap);
    }
    /*
    function pointChange(){
        index = ldata.length - 1;
        var lgroup = ldata[index];
        var sgroup = sdata[index];
        pointMark(lgroup, sgroup);
        // index = (index + 1) % ldata.length;
    }


    function pointMark(lgroup, sgroup){
        if (stoped == false){
            setTimeout(pointChange, 3000);
        }
        work_map(lgroup, myMap);
        work_list(sgroup, myMap);
    }
    */
}

var mapview = new MapView();
// var stoped = true;
// var index = 0;
var type = 2; //repost-0, origin-1, post-2, influence-3
mapview.showWholeMap();
mapview.addSwitchTabListener();
// mapview.addPauseButtonListener();
mapview.addSortChangeListener();
// getLngLat(province_list);
