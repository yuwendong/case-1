LineClusterer.prototype = new BMap.Overlay();
LineClusterer.prototype.initialize = function(){}
LineClusterer.prototype.draw = function(){}
LineClusterer.prototype.show = function(){}
LineClusterer.prototype.hide = function(){}

var STEP = 3;
var time_out_;
function LineClusterer(myMap, group){
    this.map = myMap;
    this.timeout = 250;
    this.lines = [];
    this.max_repost = 0;

    var cities;
    for (var key in group){
        cities = key.split('-');
        if ((cities[0] in city2lnglat) && (cities[1] in city2lnglat) && (group[key]["rank"] >= 1)){
            var repost_count = group[key]["count"];
            if (repost_count > this.max_repost){
                this.max_repost = repost_count;
            }

            var begin_lng = city2lnglat[cities[0]][0];
            var begin_lat = city2lnglat[cities[0]][1];
            var end_lng = city2lnglat[cities[1]][0];
            var end_lat = city2lnglat[cities[1]][1];
            var start_point = new BMap.Point(begin_lng, begin_lat);
            var end_point = new BMap.Point(end_lng, end_lat);

            var path = [];
            var delta_lng = (end_lng - begin_lng) / STEP;
            var delta_lat = (end_lat - begin_lat) / STEP;

            for (var step = 0; step < STEP; step++){
                path.push([start_point, new BMap.Point(start_point.lng + delta_lng * (step + 1), start_point.lat + delta_lat * (step + 1))]);
            }
            path.push([start_point, end_point]);
            this.lines.push({'path':path, 'repost_count':repost_count});
        }
    }
    var lines_ = [];
    var x = 0;
    var that = this;
    (function(){
        if(lines_ != []){
            for (var i = 0;i < lines_.length;i++){
                that.map.removeOverlay(lines_[i]);
            }
            lines_ = [];
        }
        for (var i = 0; i < that.lines.length; i++){
            var linecolor;
            var lineweight;
            lineweight = Math.ceil(that.lines[i].repost_count / 10);

            var unit = Math.ceil(that.max_repost / 3);
            if (!that.lines[i].repost_count || that.lines[i].repost_count <= unit){
                linecolor = 'gray';
            }
            else if (that.lines[i].repost_count > unit && that.lines[i].repost_count <= 2 * unit){
                linecolor = 'blue';
            }
            else{
                linecolor = 'red';
            }

            /*switch(that.lines[i].rank){
                case 1:linecolor = '#CC9966';break;
                case 2:linecolor = 'ffbf00';break;
                case 3:linecolor = 'gray';break;
            }
            */
            that.lines[i].polyline = new BMap.Polyline([that.lines[i].path[x][0], that.lines[i].path[x][1]], {
                strokeColor: linecolor,
                strokeOpacity: 0.5,
                strokeWeight: lineweight
            });
            lines_.push(that.lines[i].polyline);
            that.map.addOverlay(that.lines[i].polyline); //添加到地图中
            that.lines[i].polyline.disableEditing();
        }
        x++;
        time_out_ = setTimeout(arguments.callee, that.timeout);
        if (x >= STEP)
            clearTimeout(time_out_);
    })();
}
