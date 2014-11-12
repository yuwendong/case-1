
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
            // console.log("avvv");
            var select_a = $(this);
            var unselect_a = $(this).siblings('a');
            if(!select_a.hasClass('curr')) {
                select_a.addClass('curr');
                unselect_a.removeClass('curr');
                var style = select_a.attr('value');
                // console.log(style);
                getweibos_data(style);
            }
        });
         // console.log("abd");
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
        var query = QUERY;
        var end_ts = END_TS;
        // if(query=='中国'){
        var start_ts = START_TS+ 900;
        // }
        // else{
        //     var start_ts = START_TS;
        // }
        var  during_pie = end_ts-start_ts;
        var  topic = query;
        var  during = POINT_INTERVAL;
        var  limit = 50;

    function getpie_data() {
        var  style;
        var  style_list = [1,2,3];
        var  all_area = 0;
        var  all = 0;
        var  every_style = [];
        var  all_data = 0;
        var  origin_data = 0;
        var  comment_data = 0;
        var  forward_data = 0;
        var  folk = 0;
        var  media = 0;
        var  oversea = 0;
        var  opinion_leader = 0;
        var  other = 0;
        for (var i =0; i < style_list.length; i++){
                    style = style_list[i];
                    var all = 0;
            for( var time_s = 0;start_ts + time_s * during<end_ts; time_s++){
                 var ts = start_ts + time_s * during ;
                     
            $.ajax({
                url: "/propagate/total/?end_ts=" + ts + "&style=" + style +"&during="+ during + "&topic=" + topic,
                type: "GET",
                dataType:"json",
                async:false,
                success: function(data){

                    folk_value = data["dcount"];
                    folk = folk_value["folk"];

                    media_value = data["dcount"];
                    media = media_value["media"]; 
                 
                    opinion_leader_value = data["dcount"];
                    opinion_leader = opinion_leader_value["opinion_leader"]; 
                            
                    other_value = data["dcount"];
                    other = other_value["other"];
                    // console.log(other);
                
                    oversea_value = data["dcount"];
                    oversea = oversea_value["oversea"];                    
                }
            });
        all_area = folk+media+opinion_leader+other+oversea;
        all += all_area;
   
        }

                every_style.push(all);
                console.log(every_style);
            
                  }

                    for (i = 0;i<every_style.length;i++){
                      all_data += every_style[i];  
                    }
                        origin_data = (every_style[0]/all_data).toFixed(2);
                        forward_data = (every_style[1]/all_data).toFixed(2);
                        comment_data = (every_style[2]/all_data).toFixed(2);
                        console.log(origin_data);
                        console.log(forward_data);
                        console.log(comment_data);
                 on_update(origin_data,forward_data,comment_data);
}


    // var result=[];
    //     $.ajax({
    //         url: "/moodlens/pie/?ts=" + end_ts + "&query=" + query +"&during="+ during_pie,
    //         type: "GET",
    //         dataType:"json",
    //         success: function(data){
    //             console.log(data);
    //             result[0]=data["happy"];
    //             result[1]=data["sad"];
    //             result[2]=data["angry"];
    //             on_update(result);
    //         }
    //     });       
    // }
    function on_update(origin_data,forward_data,comment_data) {
        keyword_data();  
        var pie_data = [];
        // var percentage = []; 
        // console.log(result);
        // percentage[0] = String(parseFloat(result[0])*100)+"%";
        // percentage[1] = String(parseFloat(result[1])*100)+"%";
        // percentage[2] = String(parseFloat(result[2])*100)+"%";
        // console.log(percentage);

        pie_data = [{value:  origin_data, name:'原创'},{value: comment_data, name:'评论'},{value:  forward_data, name:'转发'}];
var option = {
        backgroundColor: '#FFF',
        color: ['#11c897', '#fa7256', '#6e87d7'],
        title : {
            text: '', // pie_title,
            x: 'center',
            textStyle:{
                fontWeight: 'lighter',
                fontSize: 13
            }
        },
        toolbox: {
            show: true,
            feature : {
                mark : {show: true},
                dataView : {show: true, readOnly: false},
                //magicType : {show: true, type: ['line', 'bar']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        tooltip: {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)",
            textStyle: {
                fontWeight: 'bold',
                fontFamily: 'Microsoft YaHei'
            }
        },
        legend: {
            orient:'vertical',
            x : 'left',
            data: ['原创','评论','转发'],
            textStyle: {
                fontWeight: 'bold',
                fontFamily: 'Microsoft YaHei'
            }
        },

        calculable : true,
        series : [
            {
                name: '类型占比',
                type: 'pie',
                radius : '50%',
                center: ['50%', '60%'],
                itemStyle: {
                    normal: {
                        label: {
                            position: 'inner',
                            formatter: "{d}%",
                            textStyle: {
                                fontWeight: 'bold',
                                fontFamily: 'Microsoft YaHei'
                            }
                        },
                        labelLine: {
                            show: false
                        }
                    },
                    emphasis: {
                        label: {
                            show: true,
                            formatter: "{b}\n{d}%",
                            textStyle: {
                                fontWeight: 'bold',
                                fontFamily: 'Microsoft YaHei'
                            }
                        }
                    }
                },
                data: pie_data
            }
        ],
        textStyle: {
            fontWeight: 'bold',
            fontFamily: 'Microsoft YaHei'
        }
    };

    var myChart = echarts.init(document.getElementById('pie_div'));
    myChart.setOption(option);
}
    // option = {
    //     title : {
    //         x:'center',
    //         textStyle:{
    //         fontWeight:'lighter',
    //         fontSize: 13,
    //         }        
    //     },
    //     tooltip : {
    //         trigger: 'item',
    //         formatter: "{a} <br/>{b} : {c} ({d}%)"
    //     },
    //         toolbox: {
    //     show : true,
    //     feature : {
    //         mark : {show: true},
    //         dataView : {show: true, readOnly: false},
    //         restore : {show: true},
    //         saveAsImage : {show: true}
    //     }
    // },
    //     calculable : true,
    //     series : [
    //         {
    //             name:'来源占比',
    //             type:'pie',
    //             radius : '50%',
    //             center: ['50%', '60%'],

    //             data: pie_data
    //         }
    //     ]
    // };
    // var myChart = echarts.init(document.getElementById('pie_div'));
    // myChart.setOption(option);        
    // }
    function isEmptyObject(obj){
        for ( var name in obj ) { 
            return false;
        } 
        return true; 
    } 

    function keyword_data()
    {       

        var  style = 3; 

        $.ajax({
                url:"/propagate/keywords/?end_ts=" + end_ts + "&topic=" + topic + "&during="+ during + "&limit="+ limit + "&style="+ style,
                data: "GET",
                dataType:"json",
                success: function(data)
                {   
                    // console.log(data);
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
                                            $('#keywords_cloud_div').append('<a><font color="#8E8E8E" font-weight:"lighter">'+ keyword +'</font></a>'); 
                                            }
                                }
                                on_load();
                              }
                           } 
                    })
    }   

   function getweibos_data(data){      //请求文本数据
                var selectstyle = data;
                var styleweibo = Number(data);
                // console.log(data);
                $.ajax({
                    url: "/propagate/weibos/?&topic=" + topic + "&end_ts=" + end_ts +"&limit="+limit + "&during=" + during + "&style=" + styleweibo,
                    type: "GET",
                    dataType:"json",
                    success: function(data){
                        // console.log(data);
                       $("#vertical-ticker").empty();       
                        var weibo=[];
                        for (var keyword in data[selectstyle]){
                            weibo.push(data[selectstyle][keyword]);
                            // console.log(data[selectstyle][keyword]);
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
        for (var time = 0 ; time *during + start_ts< end_ts ;time++)
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
    var atime = time;
    var deadtime = start_ts + during * atime;

    var style = 2; 
        $.ajax({
            url: "/propagate/total/?end_ts=" + deadtime + "&style=" + style +"&during="+ during + "&topic=" + topic,
            type: "GET",
            dataType:"json",
            async:false,
            success: function(data){
                 // console.log(data);

                folk_value = data["dcount"];
                folk = folk_value["folk"] 
                folk_count.push(folk);
                             
                list.push(deadtime);

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
            // console.log(list[i]);
            ns= new Date(parseInt(list[i]) * 1000).toLocaleString().substring(5,20);
            list_af.push(ns);
        }
        for (var i = 0; i < list.length; i++){
          all[i] = folk_count[i]+media_count[i]+opinion_leader_count[i]+other_count[i]+oversea_count[i];   
}
        list = [];
        $('#trend_div').highcharts({
            chart: {
            type: 'spline',
            },
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
                categories:list_af,
                labels: {
                step: 24//控制多少个点显示一个
            }
            },
            yAxis: {
                title: {
                    text: '微博条数',
                style: {
                    color: '#666',
                    fontWeight: 'bold',
                    fontSize: '12px',
                    fontFamily: 'Microsoft YaHei'
                    }
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            plotOptions: {
          spline: {
              lineWidth: 2,
              states: {
                  hover: {
                      lineWidth: 3
                  }
              },
              marker: {
                  enabled: false
              },
            }
        },
            tooltip: {
                valueSuffix: ''
            },
            legend: {
                layout: 'horizontal',
                align: 'center',
                verticalAlign: 'bottom',
                borderWidth: 0,
                borderColor: '#F0F0F0',
                itemStyle: {
                    color: '#666',
                    fontWeight: 'bold',
                    fontSize: '12px',
                    fontFamily: 'Microsoft YaHei'
                    }
            },
            series: [{
                name: '民众',
                data: folk_count,
            }, {
                name: '媒体',
                data: media_count,
            }, {
                name: '名人',
                data: opinion_leader_count,
            },
               {
                name: '海外',
                data: oversea_count,
            }, 
               {
                name: '其他',
                data: other_count,
            }]
        });
    }
function drawpicture_total_all() {
        $('#trend_div1').highcharts({
            chart: {
                type: 'spline',
            },
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
                categories: list_af,
                labels: {
                step: 24//控制多少个点显示一个
            }
            },
            yAxis: {
                title: {
                    text: '微博条数',
                style: {
                    color: '#666',
                    fontWeight: 'bold',
                    fontSize: '12px',
                    fontFamily: 'Microsoft YaHei'
                    }
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
                plotOptions: {
          spline: {
              lineWidth: 2,
              states: {
                  hover: {
                      lineWidth: 3
                  }
              },
              marker: {
                  enabled: false
              },
            }
        },
            tooltip: {
                valueSuffix: ''
            },
            legend: {
                layout: 'horizontal',
                align: 'center',
                verticalAlign: 'bottom',
                fontWeight: 'lighter',
                borderWidth: 0,
                    itemStyle: {
                    color: '#666',
                    fontWeight: 'bold',
                    fontSize: '12px',
                    fontFamily: 'Microsoft YaHei'
                    }
            },
            series: [{
                name: '全领域',
                data:all 
            }]
        });
    }
function increment_count () {
        // alert("dangqian");
        for (var time = 0 ; time *during + start_ts< end_ts ;time++)
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
    var atime = time;
    var counttime = start_ts+during * atime;
    var style = 3;     
        $.ajax({
            url: "/propagate/increment/?end_ts=" + counttime + "&style=" + style +"&during="+     during + "&topic=" + topic,
            type: "GET",
            dataType:"json",
            async:false,
            success: function(data){
                // console.log(data);
                increment_folk_value = data["dincrement"];
                increment_folk = increment_folk_value["folk"] 
                increment_folk_count.push(increment_folk);
               
              
                increment_list.push(counttime);

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

            ns= new Date(parseInt(increment_list[i]) * 1000).toLocaleString().substring(5,20);

            increment_af.push(ns);
        }
        increment_list = [];

        $('#trend_div').highcharts({
             chart: {
                type: 'spline',
            },
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
                title: {
                enabled: true,
                style: {
                color: '#666',
                fontWeight: 'bold',
                fontSize: '12px',
                fontFamily: 'Microsoft YaHei'
                    }  
                },
                categories:increment_af,
                labels: {
                step: 24//控制多少个点显示一个
            }
            },
            yAxis: {
                title: {
                    text: '增长率',
                style: {
                color: '#666',
                fontWeight: 'bold',
                fontSize: '12px',
                fontFamily: 'Microsoft YaHei'
                }
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            plotOptions: {
          spline: {
              lineWidth: 2,
              states: {
                  hover: {
                      lineWidth: 3
                  }
              },
              marker: {
                  enabled: false
              },
            }
        },
            plotOptions: {
          spline: {
              lineWidth: 2,
              states: {
                  hover: {
                      lineWidth: 3
                  }
              },
              marker: {
                  enabled: false
              },
            }
        },
            tooltip: {
                valueSuffix: ''
            },
            legend: {
                layout: 'horizontal',
                align: 'center',
                verticalAlign: 'bottom',
                borderWidth: 0,
                    itemStyle: {
                    color: '#666',
                    fontWeight: 'bold',
                    fontSize: '12px',
                    fontFamily: 'Microsoft YaHei'
                    }
            },
            series: [{
                name: '民众',
                data: increment_folk_count,
            }, {
                name: '媒体',
                data: increment_media_count,
            }, {
                name: '名人',
                data: increment_opinion_leader_count,
            }, {
                name: '海外',
                data: increment_oversea_count,
            }, {
                name: '其他',
                data: increment_other_count,
            }]
        });
    }
function drawpicture_increment_all(){

        $('#trend_div1').highcharts({
             chart: {
                type: 'spline',
            },
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
                title: {
                    enabled: true,
                style: {
                    color: '#666',
                    fontWeight: 'bold',
                    fontSize: '12px',
                    fontFamily: 'Microsoft YaHei'
                        }  
                    }, 
                categories: increment_af,
                labels: {
                step: 24//控制多少个点显示一个
            }
            },
            yAxis: {
                title: {
                    text: '增长率',
                    style: {
                        color: '#666',
                        fontWeight: 'bold',
                        fontSize: '12px',
                        fontFamily: 'Microsoft YaHei'
                        }
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
                plotOptions: {
          spline: {
              lineWidth: 2,
              states: {
                  hover: {
                      lineWidth: 3
                  }
              },
              marker: {
                  enabled: false
              },
            }
        },
            plotOptions: {
          spline: {
              lineWidth: 2,
              states: {
                  hover: {
                      lineWidth: 3
                  }
              },
              marker: {
                  enabled: false
              },
            }
        },
            tooltip: {
                valueSuffix: ''
            },
            legend: {
                layout: 'horizontal',
                align: 'center',
                verticalAlign: 'bottom',
                fontWeight: 'lighter',
                borderWidth: 0,
                itemStyle: {
                    color: '#666',
                    fontWeight: 'bold',
                    fontSize: '12px',
                    fontFamily: 'Microsoft YaHei'
                    }
            },
            series: [{
                name: '全领域',
                data:increment_total_count
            }]
        });
    }
