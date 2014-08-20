
$(document).ready(function(){   //网页加载时执行下面函数
       var style = '1';
       keyword_data();
       switch_curr_add();
       getpie_data();
       getweibos_data(style);
       bindSentimentTabClick();
    })

    function bindSentimentTabClick(){
        
        $("#Tablebselect").children("a").unbind();

        $("#Tableselect").children("a").click(function() {
            console.log("avvv");
            var select_a = $(this);
            var unselect_a = $(this).siblings('a');
            if(!select_a.hasClass('curr')) {
                select_a.addClass('curr');
                unselect_a.removeClass('curr');
                style = select_a.attr('value');
                console.log(style);
                getweibos_data(style);
            }
        });
         console.log("abd");
    }
    
    function switch_curr_add(){
        $("[name='abs_rel_switch']").bootstrapSwitch('readonly', false);
        $("[name='abs_rel_switch']").on('switchChange.bootstrapSwitch', function(event, state) {

            if (state == true){
             total_count();
            }
            else{
                increment_count();
            }
            
        });

    }
    var status;
    var result1=[];
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
                result[0]=data["happy"];
                result[1]=data["sad"];
                result[2]=data["angry"];
                on_update(result);
            }
        });       
    }
    function on_update(result) {
        keyword_data();  
        var pie_data = [];
        var percentage = []; 
        console.log(result);
        percentage[0] = String(parseFloat(result[0])*100)+"%";
        percentage[1] = String(parseFloat(result[1])*100)+"%";
        percentage[2] = String(parseFloat(result[2])*100)+"%";
        console.log(percentage);

        pie_data = [{value:  result[2], name:'转发'+percentage[2]}, {value: result[1], name:'评论'+percentage[1]}, {value:  result[0], name:'原创'+percentage[0]}];
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
    var myChart = echarts.init(document.getElementById('pie_div'));
    myChart.setOption(option);        
    }
    function isEmptyObject(obj){
        for ( var name in obj ) { 
            return false;
        } 
        return true; 
    } 

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
                                           alert(keyword);
                                            $('#keywords_cloud_div').append('<a><font color="orange" font-weight:"lighter">'+ keyword +'</font></a>'); 
                                            }
                                }
                                on_load();
                              }
                           } 
                    })
    }   

   function getweibos_data(data){      //请求文本数据
                var end_ts = 1378051200;
                var topic = "中国";
                var during = 900;
                var selectstyle = data;
                var styleweibo = Number(data);
                var limit = 50;
                console.log(data);
                $.ajax({
                    url: "/propagate/weibos/?&topic=" + topic + "&end_ts=" + end_ts +"&limit="+limit + "&during=" + during + "&style=" + styleweibo,
                    type: "GET",
                    dataType:"json",
                    success: function(data){
                        console.log(data);
                       $("#vertical-ticker").empty();       
                        var weibo=[];
                        for (var keyword in data[selectstyle]){
                            weibo.push(data[selectstyle][keyword]);
                            console.log(data[selectstyle][keyword]);
                        }
                        if(weibo.length > 0){
                             chg_weibos(weibo);
                             //console.log(weibo);
                        }
                        else{
                            $("#vertical-ticker").empty();
                            $("#vertical-ticker").append("关键微博为空！");
                        }
                    }
                });
            }

            function chg_weibos(data){     //文本写入
                var html = "";
                html += '<div class="tang-scrollpanel-wrapper" style="height: ' + 66 * data.length  + 'px;">';
                html += '<div class="tang-scrollpanel-content">';
                html += '<ul id="weibo_ul">';
                for(var i = 0; i < data.length; i += 1){
                var da = data[i];
                var uid = da['user'];
                var name;
                if ('name' in da){
                    name = da['name'];
                    if(name == 'unknown'){
                        name = '未知';
                    }
                }
                else{
                    name = '未知';
                }
                var mid = da['_id'];
                var retweeted_mid = da['retweeted_mid'];
                var retweeted_uid = da['retweeted_uid'];
                var ip = da['geo'];
                var loc = ip;
                var text = da['text'];
                var reposts_count = da['reposts_count'];
                var comments_count = da['comments_count'];
                var timestamp = da['timestamp'];
                // var date = new Date(timestamp * 1000).format("yyyy年MM月dd日 hh:mm:ss");
                var weibo_link = da['weibo_link'];
                var user_link = 'http://weibo.com/u/' + uid;
                var user_image_link = da['profile_image_url'];
                if (user_image_link == 'unknown'){
                    user_image_link = '/static/img/unknown_profile_image.gif';
                }
                html += '<li class="item"><div class="weibo_face"><a target="_blank" href="' + user_link + '">';
                html += '<img src="' + user_image_link + '">';
                html += '</a></div>';
                html += '<div class="weibo_detail">';
                html += '<p>昵称:<a class="undlin" target="_blank" href="' + user_link  + '">' + name + '</a>&nbsp;&nbsp;UID:' + uid + '&nbsp;&nbsp;于' + ip + '&nbsp;&nbsp;发布&nbsp;&nbsp;' + text + '</p>';
                html += '<div class="weibo_info">';
                html += '<div class="weibo_pz">';
                html += '<a class="undlin" href="javascript:;" target="_blank">转发(' + reposts_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
                html += '<a class="undlin" href="javascript:;" target="_blank">评论(' + comments_count + ')</a></div>';
                html += '<div class="m">';
                html += '<a class="undlin" target="_blank" href="' + weibo_link + '">' + timestamp + '</a>&nbsp;-&nbsp;';
                html += '<a target="_blank" href="http://weibo.com">新浪微博</a>&nbsp;-&nbsp;';
                html += '<a target="_blank" href="' + weibo_link + '">微博页面</a>&nbsp;-&nbsp;';
                html += '<a target="_blank" href="' + user_link + '">用户页面</a>';
                html += '</div>';
                html += '</div>';
                html += '</div>';
                html += '</li>';
            }
            html += '</ul>';
            html += '</div>';

                // for(var i=0;i<5;i+=1){

                //     var id = data[i]['_id'];
                //     var user = data[i]['user'];
                //     var user_link = 'http://weibo.com/u/'+data[i]['user'];
                //     var text = data[i]['text'];
                //     var weibo_link = data[i]['weibo_link'];
                //     var comments_count = data[i]['comments_count'];
                //     var geo = data[i]['geo'];
                //     var retweeted_text = 'None';
                //     html +="<div class=\"chartclient-annotation-title\"><a style=\"color:#000; text-decoration:none;display:inline;\" href='" + user_link + "' target='_blank' >" + user + "</a> " +  '(' + id + ')' +"发布: ";
                //     html +="<a style=\"color:#000; text-decoration:none;display:inline;\" href='" + weibo_link + "' target='_blank' >" + text + "</a></div>";
                //     if(retweeted_text != 'None'){
                //         html += "<div class=\"chartclient-annotation-content\">" + retweeted_text + "</div>";
                //                                 }
                //     html += "<div class=\"chartclient-annotation-date\"><span style=\"float:right\"> 评论数：" +  comments_count + "</span></div>";
                // } 
                $("#vertical-ticker").append(html);
            }
        var list = [];
        var list_af = [];
        var increment_af = [];

        var folk_value = [];
        var folk_count = [];
        var folk = [];
       
        var media_value = [];
        var media_count = [];
        var media = [];

        var opinion_leader_value = [];
        var opinion_leader_count = [];
        var opinion_leader = [];

        var other_value = [];
        var other_count = [];
        var other = [];

        var oversea_value = [];
        var oversea_count = [];
        var oversea = [];

        var all = [];

        var increment_list = [];
        var increment_folk_value = [];
        var increment_folk_count = [];
        var increment_folk = [];

        var increment_media_value = [];
        var increment_media_count = [];
        var increment_media = [];

        var increment_opinion_leader_value = [];
        var increment_opinion_leader_count = [];
        var increment_opinion_leader = [];

        var increment_other_value = [];
        var increment_other_count = [];
        var increment_other = [];

        var increment_oversea_value = [];
        var increment_oversea_count = [];
        var increment_oversea = [];

        var increment_total_value = [];
        var increment_total = [];
        var increment_total_count = [];
$(document).ready(function(){   //网页加载时执行下面函数
           total_count();
        })
function total_count () {
        for (time = 0 ; time < 10 ;time++)
        {
         get_count(time);
        }
        drawpicture_total();
        folk_count = [];
        media_count = [];
        opinion_leader_count = [];
        other_count = [];
        oversea_count = [];
        drawpicture_total_all();
    }
   function get_count(time){
    var during = 900;
    var atime = time;
    var end_ts = 1377998100+900 * atime;
    var topic = "中国";
    var style = 3; 
        $.ajax({
            url: "/propagate/total/?end_ts=" + end_ts + "&style=" + style +"&during="+ during + "&topic=" + topic,
            type: "GET",
            dataType:"json",
            async:false,
            success: function(data){
                folk_value = data["dcount"];
                folk = folk_value["folk"] 
                folk_count.push(folk);
                             
                list.push(end_ts);

                media_value = data["dcount"];
                media = media_value["media"] 
                media_count.push(media);

                opinion_leader_value = data["dcount"];
                opinion_leader = opinion_leader_value["opinion_leader"] 
                opinion_leader_count.push(media);
                
                other_value = data["dcount"];
                other = other_value["other"] 
                other_count.push(other);

                oversea_value = data["dcount"];
                oversea = oversea_value["oversea"] 
                oversea_count.push(oversea);
                      }
        });
}
function drawpicture_total() {
        list_af = [];
        for (var i = 0; i < list.length; i++){
            ns= new Date(parseInt(list[i]) * 1000).toLocaleString().substr(10,17);
            list_af.push(ns);
        }
        for (var i = 0; i < list.length; i++){
          all[i] = folk_count[i]+media_count[i]+opinion_leader_count[i]+other_count[i]+oversea_count[i];   
}
        list = [];
        $('#trend_div').highcharts({
            title: {
        style: { 
                fontWeight: 'lighter',
                fontSize: '13px',
                x: -20 //center
            },
                text: '',
                fontSize: '13px',
                x: -20 //center
            },
            lang: {
            printButtonTitle: "打印",
            downloadJPEG: "下载JPEG 图片",
            downloadPDF: "下载PDF文档",
            downloadPNG: "下载PNG 图片",
            downloadSVG: "下载SVG 矢量图",
            exportButtonTitle: "导出图片"
            },
            subtitle: {
              
                x: -20
            },
            xAxis: {
                categories:list_af
            },
            yAxis: {
                title: {
                    text: '微博条数'
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            tooltip: {
                valueSuffix: ''
            },
            legend: {
                layout: 'horizontal',
                align: 'center',
                verticalAlign: 'bottom',
                borderWidth: 0,
                borderColor: '#F0F0F0'
            },
            series: [{
                name: '民众',
                data: folk_count,
            }, {
                name: '媒体',
                data: media_count,
            }, {
                name: '观点领袖',
                data: opinion_leader_count,
            }, {
                name: '其他',
                data: other_count,
            },
               {
                name: '海外',
                data: oversea_count,
            }]
        });
    }
function drawpicture_total_all() {
        $('#trend_div1').highcharts({
            title: {
        style: {
                
                fontWeight: 'lighter',
                fontSize: '13px',
                x: -20 //center
            },
                text: '',
                fontSize: '13px',
                x: -20 //center
            },
            lang: {
            printButtonTitle: "打印",
            downloadJPEG: "下载JPEG 图片",
            downloadPDF: "下载PDF文档",
            downloadPNG: "下载PNG 图片",
            downloadSVG: "下载SVG 矢量图",
            exportButtonTitle: "导出图片"
            },
            subtitle: {
              
                x: -20
            },
            xAxis: {
                categories: list_af
            },
            yAxis: {
                title: {
                    text: '微博条数'
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            tooltip: {
                valueSuffix: ''
            },
            legend: {
                layout: 'horizontal',
                align: 'center',
                verticalAlign: 'bottom',
                fontWeight: 'lighter',
                borderWidth: 0
            },
            series: [{
                name: '全领域',
                data:all 
            }]
        });
    }
function increment_count () {
        alert("dangqian");
        for (time = 0 ; time < 10 ;time++)
        {
            increment_get_count(time);
        }
    drawpicture_increment();

     increment_folk_count = [];
     increment_media_count = [];
     increment_opinion_leader_count = [];         
     increment_other_count = [];
     increment_oversea_count = [];
     

     drawpicture_increment_all();
     increment_total_count = [];

     folk_count = [];
     media_count = [];
     opinion_leader_count = [];         
     other_count = [];
     oversea_count = [];
    }
   function increment_get_count(time){
    var during = 900;
    var atime = time;
    var end_ts = 1377998100+900 * atime;
    var topic = "中国";
    var style = 3;     
        $.ajax({
            url: "/propagate/increment/?end_ts=" + end_ts + "&style=" + style +"&during="+     during + "&topic=" + topic,
            type: "GET",
            dataType:"json",
            async:false,
            success: function(data){
                increment_folk_value = data["dincrement"];
                increment_folk = increment_folk_value["folk"] 
                increment_folk_count.push(increment_folk);
               
              
                increment_list.push(end_ts);

                increment_media_value = data["dincrement"];
                increment_media = increment_media_value["media"] 
                increment_media_count.push(increment_media);

                opinion_leader_value = data["dincrement"];
                opinion_leader = opinion_leader_value["opinion_leader"] 
                opinion_leader_count.push(media);
                
                increment_other_value = data["dincrement"];
                increment_other = increment_other_value["other"] 
                increment_other_count.push(increment_other);

                increment_oversea_value = data["dincrement"];
                increment_oversea = increment_oversea_value["oversea"] 
                increment_oversea_count.push(increment_oversea);

                increment_total_value = data["dincrement"];
                increment_total = increment_total_value["total"] 
                increment_total_count.push(increment_total);
            }
    });
}

function drawpicture_increment() {
        increment_af = [];
        for (var i = 0; i < increment_list.length; i++){

            ns= new Date(parseInt(increment_list[i]) * 1000).toLocaleString().substr(10,17);

            increment_af.push(ns);
        }
        increment_list = [];

        $('#trend_div').highcharts({
            title: {
        style: {
                
                fontWeight: 'lighter',
                fontSize: '13px',
                x: -20 //center
            },
                text: '',
                fontSize: '13px',
                x: -20 //center
            },
            lang: {
            printButtonTitle: "打印",
            downloadJPEG: "下载JPEG 图片",
            downloadPDF: "下载PDF文档",
            downloadPNG: "下载PNG 图片",
            downloadSVG: "下载SVG 矢量图",
            exportButtonTitle: "导出图片"
            },
            subtitle: {
              
                x: -20
            },
            xAxis: {
                categories:increment_af
            },
            yAxis: {
                title: {
                    text: '增长率'
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            tooltip: {
                valueSuffix: ''
            },
            legend: {
                layout: 'horizontal',
                align: 'center',
                verticalAlign: 'bottom',
                borderWidth: 0
            },
            series: [{
                name: '民众',
                data: increment_folk_count,
            }, {
                name: '媒体',
                data: increment_media_count,
            }, {
                name: '观点领袖',
                data: increment_opinion_leader_count,
            }, {
                name: '其他',
                data: increment_other_count,
            },
               {
                name: '海外',
                data: increment_oversea_count,
            }]
        });
    }
function drawpicture_increment_all(){

        $('#trend_div1').highcharts({
            title: {
        style: {
                fontWeight: 'lighter',
                fontSize: '13px',
                x: -20 //center
            },
                text: '',
                fontSize: '13px',
                x: -20 //center
            },
            lang: {
            printButtonTitle: "打印",
            downloadJPEG: "下载JPEG 图片",
            downloadPDF: "下载PDF文档",
            downloadPNG: "下载PNG 图片",
            downloadSVG: "下载SVG 矢量图",
            exportButtonTitle: "导出图片"
            },
            subtitle: {
              
                x: -20
            },
            xAxis: {
                categories: increment_af
            },
            yAxis: {
                title: {
                    text: '增长率'
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            tooltip: {
                valueSuffix: ''
            },
            legend: {
                layout: 'horizontal',
                align: 'center',
                verticalAlign: 'bottom',
                fontWeight: 'lighter',
                borderWidth: 0
            },
            series: [{
                name: '全领域',
                data:increment_total_count
            }]
        });
    }
