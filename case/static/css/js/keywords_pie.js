$(document).ready(function(){   //网页加载时执行下面函数
           getpie_data();
           keyword_data();
        })
    var query = "中国";
    var ts = 1378035900;
    var START_TS = 1377965700;
    var during = ts-START_TS;
    function getpie_data() {
        var result=[];
        $.ajax({
            url: "/moodlens/pie/?ts=" + ts + "&query=" + query +"&during="+ during,
            type: "GET",
            dataType:"json",
            success: function(data){
                // console.log(data);
                result[0]=data["happy"];
                //console.log(data['happy']);
                //alert("result[0]");
                result[1]=data["sad"];
                result[2]=data["angry"];
                on_update(result);
            }
        });       
    }
    function on_update(result) {
    //alert('on_update' + result[0]);
    //alert('on_update' + result[1]);
    //alert('on_update' + result[2]);
        //result1=getpie_data(); 
        var pie_data=[];
        pie_data = [{value:  result[2], name:'1'}, {value: result[1], name:'2'}, {value:  result[0], name:'3'}];

    option = {
        title : {
            x:'center',
            textStyle:{
            fontWeight:'lighter',
            fontSize: 13,
            }        
        },
        tooltip : {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)"
        },
        legend: {
            orient:'vertical',
            x : 'left',
            data:['1','2','3']
        },
            toolbox: {
        show : true,
        feature : {
            mark : {show: true},
            dataView : {show: true, readOnly: false},
            restore : {show: true},
            saveAsImage : {show: true}
        }
    },
        calculable : true,
        series : [
            {
                name:'访问来源',
                type:'pie',
                radius : '50%',
                center: ['50%', '60%'],
                data: pie_data
            }
        ]
    };
    var myChart = echarts.init(document.getElementById('pie'));
    myChart.setOption(option);        
    }
  
    function isEmptyObject(obj){
        for ( var name in obj ) { 
            return false;
        } 
        return true; 
    } 
           $(document).ready(function(){   //网页加载时执行下面函数
           keyword_data();
        })
    function keyword_data()
    {       
        var  topic = "中国";
        var  end_ts = 1377965700;
        var  during = 900;
        var  limit = 50;
        var  style = 3; 
        $.ajax({
                url:"/propagate/keywords/?end_ts=" + end_ts + "&topic=" + topic + "&during="+ during + "&limit="+ limit + "&style="+ style,
                data: "GET",
                dataType:"json",
                success: function(data)
                {   
                            if(data=='search function undefined'){
                                $("#keywords_cloud_div").empty();
                                $("#keywords_cloud_div").append("<a style='font-size:1ex'>关键词云数据为空</a>");  
                            }
                            else{
                                if(isEmptyObject(data)){
                                    $("#keywords_cloud_div").empty();
                                    $("#keywords_cloud_div").append("<a style='font-size:1ex'>关键词云数据为空</a>");   
                                }
                                else{ 
                                        for(var keyword in data){
                                           // alert(keyword);
                                            $('#keywords_cloud_div').append('<a><font color="#FF79BC" font-weight:"lighter">'+ keyword +'</font></a>'); 
                                            }
                                }

                                 on_load();
                              }
                           } 
                    })
    }   