var province_list = ["安徽", "北京", "重庆", "福建", "甘肃", "广东", "广西", "贵州", "海南", "河北", "黑龙江", "河南", "湖北", "湖南", "内蒙古", "江苏", "江西", "吉林", "辽宁", "宁夏", "青海", "山西", "山东", "上海", "四川", "天津", "西藏", "新疆", "云南", "浙江", "陕西", "台湾", "香港", "澳门"];
function getLngLat(province_list){
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
}
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
    this.myMap.addControl(new BMap.MapTypeControl());
    this.myMap.addControl(new BMap.NavigationControl());
    this.myMap.addControl(new BMap.ScaleControl());
    this.myMap.addControl(new BMap.OverviewMapControl());
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

    for (var i = 0; i < ldata.length; i++){
        var group = ldata[i];
        var cities = [];
        for (var key in group){
            cities = key.split('-');
            origin_point = new BMap.Point(city2lnglat[cities[0]][0], city2lnglat[cities[0]][1]);
            repost_point = new BMap.Point(city2lnglat[cities[1]][0], city2lnglat[cities[1]][1]);
            var points = [origin_point, repost_point];
            var curve = new BMapLib.CurveLine(points, {strokeColor:"blue", strokeWeight:3, strokeOpacity:0.5}); //创建弧线对象
            myMap.addOveirlay(curve); //添加到地图中
            curve.enableEditing(); //开启编辑功能

        }
    }
    // var beijingPosition=new BMap.Point(116.432045,39.910683),hangzhouPosition=new BMap.Point(120.129721,30.314429),
    //                     taiwanPosition=new BMap.Point(121.491121,25.127053);
    // var points = [beijingPosition,hangzhouPosition, taiwanPosition];


}

var mapview = new MapView();
mapview.showWholeMap();
// getLngLat(province_list);
