
$(document).ready(function(){   //网页加载时执行下面函数
           // gettext_data();
            writ_text();
            getindex_data();


        })
    // var query =QUERY;
    // var topic = query;

    //     var start_ts = START_TS + 900;
   
    // var end_ts =  END_TS;
    // var during = POINT_INTERVAL;
    var topic = QUERY;
    if(topic == '中国'){
      var start_ts = 1377964800 + 900;
    }
    else{
      var start_ts = START_TS;
    }
    var end_ts = END_TS;
    
    function gettext_data() {
        var result=[];
        $.ajax({
            url: "/index/gaishu_data/?query=" + query,
            type: "GET",
            dataType:"json",
            success: function(data){
                writ_text();
                bindTabClick();
                $("#summary_tooltip").tooltip();
            }
        });       
    }
       function bindTabClick(){
        
        $("#Tablebselect").children("a").unbind();

        $("#Tableselect").children("a").click(function() {
            console.log("abc");
            var select_a = $(this);
            var unselect_a = $(this).siblings('a');
            if(!select_a.hasClass('curr')) {
                select_a.addClass('curr');
                unselect_a.removeClass('curr');
                style = select_a.attr('value');
              
                // getweibos_data(style);

            }
        });
    }

    function writ_text(){
        var html = '';
        //data['tag']表示的是事件的标签
        html += '<h4><b>事件标签:'+'东盟,博览会'+'</b></h4><br/>';
        html += '<h4 style="padding-top:10px"><b>事件摘要</b></h4>';
        html += '<i id=\"media_tooltip\" class=\"glyphicon glyphicon-question-sign\" data-toggle=\"tooltip\" data-placement=\"left\" title=\"事件总体概述\"></i>&nbsp;&nbsp;'
        // html += '<span class="pull-right" style="margin: -10px auto -10px auto;">';
        // html += '<input type="checkbox" name="abs_rel_switch" checked></span>';
        $('#title_text').append(html);
        // var keyhtml = '';  

        // keyhtml += '<h5 style="padding-top:5px;margin-left:20px"><b>时间关键字:</b>'
        // // console.log(data['key_words']);
        // for(var k in data['key_words']){
        //     keyhtml += k+',';
        // }
        // keyhtml +='</h5>';        
        // $('#tabkeywords').append(keyhtml);
        
        var content = '';
        // var begin = new Date(parseInt(data['begin']) * 1000).toLocaleString().replace(/年|月/g, "-").replace(/日/g, " ").replace(/上午/g,'');
        // var end = new Date(parseInt(data['end']) * 1000).toLocaleString().replace(/年|月/g, "-").replace(/日/g, " ").replace(/上午/g,'');
        content += ' <p style="padding-top:25px ;text-indent:2em">该事件发生于' + '<b style="background:#ACD6FF  ">'+'2013-9-2'+'</b>' + '，事件发生地点为' +'<b style="background:#ACD6FF  ">广西南宁</b>'  + '。' ;
        content += '该事件的舆情信息起始于' + '<b style="background:#ACD6FF  ">'+'2013-9-2'+'</b>' + '，终止于' + '<b style="background:#ACD6FF  ">'+'2013-9-7'+'</b>';
        content += '，共' +'3000' + '人参与信息发布与传播，' + '舆情信息累计' + '200'+ '条。';
        content += '参与人群集中于' + '<b style="background:#ACD6FF  ">'+'北京，上海，广州，广西，山东，浙江，江苏， 河南， 湖北， 湖南' +'</b>'+ '。';
        content += ' 前' + '<b style="background:#ACD6FF  ">10</b>个关键词是：东盟，总理，高科技，中国，博览会，力量，李克强，国际，十年，合作';
        content += '。';
        content += '' + '网民情绪分布情况为：积极：60%，愤怒：23%，悲伤：17%' ;
        content +=  '。</p>';
        $("#keywords_text").append(content);
        identify_request() ;
        //draw_line()画曲线的
    }

    function request_callback(data) {
        rankdata = data;
        var status = 'current finished';
        var page_num = 10 ;
        if (status == 'current finished') {
            $("#current_process_bar").css('width', "100%")
            $("#current_process").removeClass("active");
            $("#current_process").removeClass("progress-striped");
            current_data = data;
            if (current_data.length) {
                $("#loading_current_data").text("计算完成!");
                if (current_data.length < page_num) {
                    page_num = current_data.length
                    create_current_table(current_data, 0, page_num, 'pro');
                }
                else {
                    create_current_table(current_data, 0, page_num, 'pro');
                    var total_pages = 0;
                    if (current_data.length % page_num == 0) {
                        total_pages = current_data.length / page_num;
                    }
                    else {
                        total_pages = current_data.length / page_num + 1;
                    }
            
                    $('#rank_page_selection').bootpag({
                        total: total_pages,
                        page: 1,
                        maxVisible: 30
                    }).on("page", function(event, num){
                        start_row = (num - 1)* page_num;
                        end_row = start_row + page_num;
                        if (end_row > current_data.length)
                            end_row = current_data.length;
                            create_current_table(current_data, start_row, end_row, 'pro');
                    });
                }
            }
            else {
                $("#loading_current_data").text("很抱歉，本期计算结果为空!");
            }
        }
        else{
            return
        }
    }

function filter_node_in_network(node_uid){
    show_network();
    filter
      .undo('filter_node')
      .nodesBy(function(n) {
        return n.label == String(node_uid);
      }, 'filter_node')
      .apply();
}
    
    function create_current_table(data, start_row, end_row, type) {
    if(type == 'pro'){
      $("#rank_table").empty();
    }
    else{
      $("#rank_table_source").empty();
    }

    var cellCount = 10;
    var table = '<table class="table table-bordered">';
    if (type == 'pro'){
     var thead = '<thead><tr><th>排名</th><th style="display:none">博主ID<th>博主昵称</th><th>博主地域</th><th>粉丝数</th><th>关注数</th><th>PR值  <b>↓</b></th><th>度中心性</th><th>介数中心性</th><th>紧密中心性</th></tr></thead>';   
    }
    else{
    var thead = '<thead><tr><th>排名</th><th style="display:none">博主ID<th>博主昵称</th><th>博主地域</th><th>粉丝数  <b>↓</b></th><th>关注数</th><th>PR值 </th><th>度中心性</th><th>介数中心性</th><th>紧密中心性</th></tr></thead>';    
    }
    
    var tbody = '<tbody>';
    console.log(data);
    for (var i = start_row;i < end_row;i++) {
      var tr = '<tr>';
      for(var j = 0;j < cellCount;j++) {
        if(j == 0) {
          // rank status
          var td = '<td><span class="label label-important">'+data[i][j]+'</span></td>';
        }
        else if(j == 1){
            var td = '<td style="display:none">'+data[i][j]+'</td>';
        }
        else if(j == 2){
            var t = j-1;
            var td = '<td><a href=\"http://weibo.com/u/' + data[i][t] + '\" >' + data[i][j] + '</a></td>';
        }
        else if(j == 3){
            var td = '<td>' + data[i][j] + '</a></td>';
        }
        else if(j == 4){
            var td = '<td>' + data[i][j] + '</a></td>';
        }
        else if(j == 5){
            var td = '<td>' + data[i][j] + '</a></td>';
        }
        else{
            var td = '<td>'+data[i][j].toFixed(3)+'</td>';
        }
        tr += td;
      }
      tr += '</tr>';
      tbody += tr;
    }
    tbody += '</tbody>';
    table += thead + tbody;
    table += '</table>';

    if(type == 'pro'){
      $("#rank_table").html(table);
    }
    else{
      console.log(table);
      $("#rank_table_source").html(table);
    }
}


function identify_request() {
  var topn = 100;
  $.get("/identify/rank/", {'topic': topic, 'start_ts': start_ts, 'end_ts': end_ts ,"topn" : topn}, request_callback, "json");
}

function identify_origin_request(){
  $.get("/identify/origin/", {'topic': topic, 'start_ts': start_ts, 'end_ts': end_ts}, origin_request_callback, "json");
}

function origin_request_callback(data) {
    rankdata = data;
    var status = 'current finished';
    var page_num = 10 ;
    if (status == 'current finished') {
        $("#current_process_bar").css('width', "100%")
        $("#current_process").removeClass("active");
        $("#current_process").removeClass("progress-striped");
        current_data = data;
        if (current_data.length) {
            $("#loading_current_data_source").text("计算完成!");
            if (current_data.length < page_num) {
                page_num = current_data.length
                create_current_table(current_data, 0, page_num, 'source');
            }
            else {
                create_current_table(current_data, 0, page_num, 'source');
                var total_pages = 0;
                if (current_data.length % page_num == 0) {
                    total_pages = current_data.length / page_num;
                }
                else {
                    total_pages = current_data.length / page_num + 1;
                }
        
                $('#rank_page_selection_source').bootpag({
                    total: total_pages,
                    page: 1,
                    maxVisible: 30
                }).on("page", function(event, num){
                    start_row = (num - 1)* page_num;
                    end_row = start_row + page_num;
                    if (end_row > current_data.length)
                        end_row = current_data.length;
                        create_current_table(current_data, start_row, end_row, 'source');
                });
            }
        }
        else {
            $("#loading_current_data_source").text("很抱歉，本期计算结果为空!");
        }
    }
    else{
        return
    }
}

identify_request();
identify_origin_request();


    // function identify_request() {
    //   var topn = 10;
    //   $.get("/identify/rank/", {'topic': topic, 'start_ts': start_ts, 'end_ts': end_ts ,"topn" : topn}, request_callback, "json");
    // }
    
    // function request_callback(data) {
    //             console.log(data);
    //     $("#rank_table").empty();
    //     var cellCount = 10;
    //     var table = '<table class="table table-bordered">';
    //     var thead = '<thead><tr><th>排名</th><th style="display:none">博主ID</th><th>博主昵称</th><th>博主地域</th><th>粉丝数</th><th>关注数</th><th>Pagerank值</th><th>度中心性</th><th>介数中心性</th><th>紧密中心性</th></tr></thead>';
    //     var tbody = '<tbody>';
    //     console.log("123");
    //     for (var i = 0;i < data.length;i++) {
    //         var tr = '<tr>';
    //               for(var j = 0;j < cellCount;j++) {
    //         if(j == 0) {
    //           // rank status
    //           var td = '<td><span class="label label-important">'+data[i][j]+'</span></td>';
    //       }
    //       else if(j == 1){
    //           var td = '<td style="display:none">'+data[i][j]+'</td>';
    //       }
    //       else if(j == 2){
    //         // if(name == 'unknown'){
    //         //     name = '未知';
    //         // }
       
    //           var td = '<td><a target=\"_blank\" onclick=\"filter_node_in_network(' + data[i][1] + ')\">' + data[i][j] + '</a></td>';
    //       }
    //       else{
    //           var td = '<td>'+data[i][j]+'</td>';
    //       }
    //       tr += td;
    //               }
    //         tr += '</tr>';
    //         tbody += tr;
    //     }
    //     tbody += '</tbody>';
    //     table += thead + tbody;
    //     table += '</table>'
    //     $("#rank_table").html(table);
    // }

    //开始画总量和消极情绪的曲线
//             var happy_count = [];
//             var sad_count = [];
//             var angry_count = [];
//             var total_count = [];
//             var stramp_count = [];
//             var stramp = [];
//             var happy = [];
//             var sad = [];
//             var angry = [];


//             var folk_value = [];
//             var folk_count = [];
//             var folk = [];
           
//             var media_value = [];
//             var media_count = [];
//             var media = [];

//             var opinion_leader_value = [];
//             var opinion_leader_count = [];
//             var opinion_leader = [];

//             var other_value = [];
//             var other_count = [];
//             var other = [];

//             var oversea_value = [];
//             var oversea_count = [];
//             var oversea = [];

//             var total = [];
//             var total_allarea = [];
//         function draw_line(){

//             var emotion_type = "global";
//             var names = {'happy': '高兴','angry': '愤怒','sad': '悲伤'};

//             for( var time_s = 0;start_ts + time_s * during<end_ts; time_s++){
//                 var ts = start_ts + time_s * during ;
//                 var ajax_url = "/moodlens/data/?ts=" + ts + '&during=' + during + '&emotion=' + emotion_type + '&query=' + query;
//                 $.ajax({
//                     url: ajax_url,
//                     type: "GET",
//                     dataType:"json",
//                     async:false,
//                     success: function(data){
//                         // console.log(data);
//                         happy = data['happy'][1]; 
//                         var ns =  data['happy'][0]; 
//                         // console.log(ns);                   
//                         stramp =  new Date(ns).toLocaleString().replace(/年|月/g, ".").replace(/日/g, " ").replace(/上午/g, "").replace(/下午/g, "").substring(5,20);                      
//                         sad = data['sad'][1];
//                         angry = data['angry'][1];
//                         total =  sad + angry;
//                          stramp_count.push(stramp);
//                          happy_count.push(happy);
//                          angry_count.push(angry);
//                          sad_count.push(sad);
//                          total_count.push(total); 
//                         // for(var name in names){
//                         //     var count = data[name][1];
//                         //     if(name in data){
                                
//                         //         // console.log(name);
   
//                         //         if(name = 'happy'){
//                         //         happy_count.push(count); 
//                         //          // console.log(happy_count);                              
//                         //     }
//                         //         if(name = 'angry'){
//                         //         angry_count.push(count);
//                         //     }
//                         //         if(name = 'sad'){
//                         //         sad_count.push(count);
//                         //     }
//                         //         }                           
//                         // }
//                     }

//                 });
//            }
//     var style;
//     var style_list = [1,2,3];
   
//     for( var time_s = 0;start_ts + time_s * during<end_ts; time_s++){
//          var ts = start_ts + time_s * during ;
//              var all = 0;
//         for (var i =0; i < style_list.length; i++){
//             style = style_list[i];

//         $.ajax({
//             url: "/propagate/total/?end_ts=" + ts + "&style=" + style +"&during="+ during + "&topic=" + topic,
//             type: "GET",
//             dataType:"json",
//             async:false,
//             success: function(data){
//                 console.log(data);

//                 folk_value = data["dcount"];
//                 folk = folk_value["folk"];


//                 media_value = data["dcount"];
//                 media = media_value["media"]; 
             
//                 opinion_leader_value = data["dcount"];
//                 opinion_leader = opinion_leader_value["opinion_leader"]; 
                        
//                 other_value = data["dcount"];
//                 other = other_value["other"];
            
//                 oversea_value = data["dcount"];
//                 oversea = oversea_value["oversea"]; 
                
//             }
//         });
//         all_area = folk+media+opinion_leader+other+oversea;
//         all += all_area;

//         }
//                 total_allarea.push(all);
            
//                   }
//                   drawpicture(stramp_count,total_count,total_allarea);
//    }
//  function drawpicture(stramp_count,total_count,total_allarea){
//     $('#line').highcharts({
//         chart: {
//             type: 'spline',
         
//         },
//         title: {
//             text: '',
//             x: -20 //center
//         },
//         subtitle: {
//             text: '',
//             x: -20
//         },
//         xAxis: {
//             title: {
//                     enabled: true,
//                 style: {
//                     color: '#666',
//                     fontWeight: 'bold',
//                     fontSize: '12px',
//                     fontFamily: 'Microsoft YaHei'
//                         }  
//                     }, 
//             categories: stramp_count,

                
//             labels: {
//                 step: 24//控制多少个点显示一个
//             }
//           },
//         yAxis: {
//             title: {
//                 text: '条',
//         style: {
//                 color: '#666',
//                 fontWeight: 'bold',
//                 fontSize: '12px',
//                 fontFamily: 'Microsoft YaHei'
//                 }
//             },
//             plotLines: [{
//                 value: 0,
//                 width: 1,
//                 color: '#808080'
//             }]
//         },
//         plotOptions: {
//           spline: {
//               lineWidth: 2,
//               states: {
//                   hover: {
//                       lineWidth: 3
//                   }
//               },
//               marker: {
//                   enabled: false
//               },
//             }
//         },
//         tooltip: {
//             valueSuffix: '条'
//         },
//         legend: {
//             layout: 'horizontal',
//             align: 'center',
//             verticalAlign: 'bottom',
//             borderWidth: 0,
//         itemStyle: {
//             color: '#666',
//             fontWeight: 'bold',
//             fontSize: '12px',
//             fontFamily: 'Microsoft YaHei'
//             }
//         },
//         series: [{
//             name: '消极',
//             data: total_count
//         },{
//             name: '微博总数',
//             data: total_allarea
//         }]
//     });
// }

//总量和消极情绪曲线结束


    //开始微博分页

    // function weibo_page(data){          //关键微博翻页函数
    //     console.log(data);
    //     var current_data = data;
    //     var page_num = 10;
    //     if (current_data['opinion'].length) {
    //         if (current_data['opinion'].length < page_num) {
    //             page_num = current_data['opinion'].length;
    //             writ_opinion(current_data, 0 ,page_num);
    //             //create_current_table(current_data, 0, page_num);
    //         }
    //         else {
    //             writ_opinion(current_data, 0, page_num);
    //             var total_pages = 0;
    //             if (current_data['opinion'].length % page_num == 0) {
    //                 total_pages = current_data['opinion'].length / page_num;
    //             }
    //             else {
    //                 total_pages = current_data['opinion'].length / page_num + 1;
    //             }
    //             $('#rank_page_selection').bootpag({
    //               total: total_pages,
    //               page: 1,
    //               maxVisible: 30
    //             }).on("page", function(event, num){
    //               var start_row = (num - 1)* page_num;
    //               var end_row = start_row + page_num;
    //               if (end_row > current_data['opinion'].length)
    //                   end_row = current_data['opinion'].length;
    //               writ_opinion(current_data, start_row, end_row);
    //             });
    //         }
    //     }

    // } 

    //结束微博的分页
    //开始读取微博
    // function writ_opinion(data , begin, end ){

    //     var opinion;
    //     var html = "";
    //     html += '<div class="tang-scrollpanel-wrapper" style="height: ' + 66 * data.length  + 'px;">';
    //     html += '<div class="tang-scrollpanel-content">';
    //     html += '<ul id="weibo_ul">';

    //     for (var op = begin ; op <= end ; op++){             //一条条读取微博
    //             var sop = op.toString();

    //             opinion= data['opinion'][sop];
    //             var name = opinion['username'];
    //             var mid = opinion['user'];
    //             var ip = opinion['geo'];
    //             var loc = ip;
    //             var text = opinion['text'];
    //             var comments_count = opinion['comments_count'];
    //             // var timestamp = opinion['timestamp'];
    //             // console.log(timestamp);
    //             var timestamp = new Date(parseInt(opinion['timestamp']) * 1000).toLocaleString().replace(/年|月/g, "-").replace(/日/g, " ").replace(/上午/g,'')
    //             var user_link = 'http://weibo.com/u/' + mid;
    //             var user_image_link = opinion['profile_image_url'];
    //             if (user_image_link == 'unknown'){
    //                 user_image_link = '/static/img/unknown_profile_image.gif';
    //             }
    //             html += '<li class="item"><div class="weibo_face"><a target="_blank" href="' + user_link + '">';
    //             html += '<img src="' + user_image_link + '">';
    //             html += '</a></div>';
    //             html += '<div class="weibo_detail">';
    //             html += '<p>昵称:<a class="undlin" target="_blank" href="' + user_link  + '">' + name + '</a>&nbsp;&nbsp;UID:' + mid + '&nbsp;&nbsp;于' + ip + '&nbsp;&nbsp;发布&nbsp;&nbsp;' + text + '</p>';
    //             html += '<div class="weibo_info">';
    //             html += '<div class="weibo_pz">';
    //             html += '<a class="undlin" href="javascript:;" target="_blank">评论(' + comments_count + ')</a></div>';
    //             html += '<div class="m">';
    //             html += '<a class="undlin" target="_blank">' + timestamp + '</a>&nbsp;-&nbsp;';
    //             html += '<a target="_blank" href="http://weibo.com">新浪微博</a>&nbsp;-&nbsp;';
    //             html += '<a target="_blank" href="' + user_link + '">用户页面</a>';
    //             html += '</div>';
    //             html += '</div>';
    //             html += '</div>';
    //             html += '</li>';
    //         }            
    //         html += '</ul>';
    //         html += '</div>';
    //         html += '</div>';
    //         $("#opinion_text").empty();
    //         $("#opinion_text").append(html);

    //     }
    //微博读取结束
 function draw_line(last_index,f_sensitivity,f_sentiment,f_transmission,f_involved){  
 console.log();                                                            
    $('#bar_div').highcharts({                                           
        chart: {                                                           
            type: 'bar'                                                    
        },                                                                 
        title: {                                                           
            text: ''                    
        },                                                                 
        subtitle: {                                                        
            text: ''                                  
        },                                                                 
        xAxis: {                                                           
            categories: ['舆情指数', '事件敏感指数', '负面情绪指数','传播强度指数','主体敏感指数'],
            title: {                                                       
                text: null                                                 
            }                                                              
        },                                                                 
        yAxis: {                                                           
            min: 0,                                                        
            title: {                                                       
                text: '',                             
                align: 'high'                                              
            },                                                             
            labels: {                                                      
                overflow: 'justify'                                        
            }                                                              
        },                                                                 
        tooltip: {                                                         
            valueSuffix: ' '                                       
        },        
        plotOptions: {
            series: {
                pointWidth: 10,
                pointPadding: 1,
                groupPadding: 0,
                borderWidth: 0,
                shadow: false
            }
        },
                                                                 
        legend: {                                                          
            layout: 'vertical',                                            
            align: 'right',                                                
            verticalAlign: 'top',                                          
            x: -40,                                                        
            y: 100,                                                        
            floating: true,                                                
            borderWidth: 1,                                                
            backgroundColor: '#FFFFFF',                                    
            shadow: true                                                   
        },                                                                 
        credits: {                                                         
            enabled: false                                                 
        },                                                                 
        series: [{                                                         
            name: '事件指标', 
            // {'color':'blue','y':ast_index}, 
            // {'color':'#FF2D2D','y':f_sensitivity}, 
            // {'color':'#FF2D2D','y':f_sentiment}, 
            // {'color':'#FF2D2D','y':f_transmission}, 
            // {'color':'#FF2D2D','y':f_involved},                            
            data: [last_index,f_sensitivity,f_sentiment,f_transmission,f_involved],
            color: '#FF2D2D'                               
        }]                                                                 
    });                                                                    
}
   


     function getindex_data(){
        $.ajax({
        url:"/quota_system/topic/?topic="+topic,
        dataType: "json",
        type: "GET",
        success :function(data){            
            console.log(data);
             var last_index = data["last_index"]; 
             var f_quota_evolution = data['f_quota_evolution'];           
             var f_involved = f_quota_evolution['f_involved'][0];
             var f_sensitivity = f_quota_evolution['f_sensitivity'][0];
             var f_sentiment = f_quota_evolution['f_sentiment'][0];
             var f_transmission = f_quota_evolution['f_transmission'][0];
             draw_line(last_index,f_sensitivity,f_sentiment,f_transmission,f_involved);   
        }       
    });
}
