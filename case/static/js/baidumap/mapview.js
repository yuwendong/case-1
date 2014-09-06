 var province_list = ["安徽", "北京", "重庆", "福建", "甘肃", "广东", "广西", "贵州", "海南", "河北", "黑龙江", "河南", "湖北", "湖南", "内蒙古", "江苏", "江西", "吉林", "辽宁", "宁夏", "青海", "山西", "山东", "上海", "四川", "天津", "西藏", "新疆", "云南", "浙江", "陕西", "台湾", "香港", "澳门"];
/*function getLngLat(province_list){
    var index = 0;
    var myGeo = new BMap.Geocoder();
    var adds = province_list;
    bdGEO();

    function bdGEO(){
        var add = adds[index];
        geocodeSearch(add);
        index++;
    }
    function geocodeSearch(add){
        if (index < adds.length){
            setTimeout(bdGEO,400);
        }
        myGeo.getPoint(add, function(point){
            if (point){
                console.log(index +"、" + add + ":" + point.lng + "," + point.lat);
            }
        });
    }
}*/

function MapView(){
    this.query = '中国';
    this.map_div_id = "allmap";
    this.ajax_method = "GET";
    this.myMap;

}
MapView.prototype.disposeMyMap = function(){
    if (this.myMap){
        this.reset();
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
    this.myMap.enableScrollWheelZoom(true);
}
MapView.prototype.initPullDrawMap = function(){
    var ajax_url = this.whole_map_ajax_url(this.query);
    var myMap = new BMap.Map(document.getElementById(this.map_div_id));
    this.myMap = myMap;
    this.initMap();

    var that = this;
    this.call_async_ajax_request(ajax_url, this.ajax_method, callback);

    function callback(data){
        drawWholeMap(that, data);
    }
}
MapView.prototype.showWholeMap = function(){
    this.disposeMyMap();
    this.initPullDrawMap();
}

function drawWholeMap(that, data){
    var myMap = that.myMap;
    var ldata = data.draw_line_data;
    var index = 0;
    pointChange();

    function pointChange(){
        var group = ldata[index];
        pointMark(group);
        index = (index + 1) % ldata.length;
    }

    function pointMark(group){
        if (index < ldata.length){
            setTimeout(pointChange, 1000);
            myMap.clearOverlays();

            var cities = [];
            var markers = [];
            var STEP = 3;

            for (var key in group){
                cities = key.split('-');
                if ((cities[0] in city2lnglat) && (cities[1] in city2lnglat) && (group[key]["rank"] == 3)){
                    var begin_lng = city2lnglat[cities[0]][0];
                    var begin_lat = city2lnglat[cities[0]][1];
                    var end_lng = city2lnglat[cities[1]][0];
                    var end_lat = city2lnglat[cities[1]][1];

                    var delta_lng = (end_lng - begin_lng) / STEP;
                    var delta_lat = (end_lat - begin_lat) / STEP;

                    /*for (step = 0; step < STEP; step++){
                        var a_lng = begin_lng + delta_lng * step;
                        var a_lat = begin_lat + delta_lat * step;
                        var a_point = new BMap.Point(a_lng, a_lat);

                        var b_lng = a_lng + delta_lng;
                        var b_lat = a_lat + delta_lat;
                        var b_point = new BMap.Point(b_lng, b_lat);

                        var points = [a_point, b_point];
                        var polyline = new BMap.Polyline(points, {strokeColor:"gray", strokeWeight:1, strokeOpacity:0.5});

                        myMap.addOverlay(polyline); //添加到地图中
                        polyline.disableEditing();
                    }
                    */
                    var origin_point = new BMap.Point(begin_lng, begin_lat);
                    var repost_point = new BMap.Point(end_lng, end_lat);
                    var points = [origin_point, repost_point];
                    var polyline = new BMap.Polyline(points, {strokeColor:"gray", strokeWeight:1, strokeOpacity:0.5});

                    myMap.addOverlay(polyline); //添加到地图中
                    polyline.disableEditing();
                    markers.push(new BMap.Marker(origin_point));
                    markers.push(new BMap.Marker(repost_point));
                }
            }
            var markerClusterer = new BMapLib.MarkerClusterer(myMap, {markers: markers});
        }
        /* function pointSet(){
            console.log(step + ":" + a_lng + "," + a_lat + ";" + b_lng + "," + b_lat);
            pointDraw(a_point, b_point);
            step++;
        }*/
        /*function pointDraw(a_point, b_point){
            if (step < STEP){
                setTimeout(pointSet, 100);

            }
        }*/
    }
}

var mapview = new MapView();
mapview.showWholeMap();
// getLngLat(province_list);
