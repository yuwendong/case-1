var dataMap = {};
var topic = "中国";
var style = 1;
var during = 1800;
var codenum = 4;
var ts_list=[];
var mappoint_data;
function dataFormatter(obj) {
    var pList = ['安徽','北京','重庆','福建','甘肃','广东','广西','贵州','海南','河北','黑龙江','河南','湖北','湖南','内蒙古','江苏','江西','吉林','辽宁','宁夏','青海','山西','山东','上海','四川','天津','西藏','新疆','云南','浙江','陕西','台湾','香港','澳门'];
    var temp;
    //console.log(obj);
    for (var year in obj) {
        temp = obj[year];
        for (var i = 0, l = temp.length; i < l; i++) {

            obj[year][i] = {
                name : pList[i],
                value : temp[i]
            }
        }
    }
    //console.log(obj);  
    return obj;
}
function dataMix(list) {
    var mixData = {};
    for (var i = 0, l = list.length; i < l; i++) {
        for (var key in list[i]) {
            if (list[i][key] instanceof Array) {
                mixData[key] = mixData[key] || [];
                for (var j = 0, k = list[i][key].length; j < k; j++) {
                    mixData[key][j] = mixData[key][j] 
                                      || {name : list[i][key][j].name, value : []};
                    mixData[key][j].value.push(list[i][key][j].value);
                }
            }
        }
    }
    return mixData;
}

  function map(ots){
    //  var atime = time;
    var ts=ots;

     $.ajax({
            url: "/evolution/topic_ajax_spatial/?ts=" + ts + '&topic=' + topic + '&style=' + style + '&codenum=' + codenum,
            type: "GET",
            dataType:"json",
            async: false,
            
            success: function(data){
                
                 console.log(data);
                 mappoint_data=data["count"];

                // console.log(mappoint_data);

                 
                 dataMap.dataweibo = dataFormatter(mappoint_data);

            }
        });

    }


    function get_time(){

        console.log(mappoint_data);

        for (var keyword in mappoint_data){

            ts_list.push(keyword);
        }

        //console.log(ts_list);

        return ts_list;
    }

