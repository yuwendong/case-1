
$(document).ready(function(){   //网页加载时执行下面函数
           gettext_data();
        })
    var query =QUERY;
    var topic = query;
    if(query=='中国'){
        var start_ts = 1377997200 + 900;
    }
    else{
        var start_ts = START_TS;
    }
    var end_ts =  END_TS;
    var during = POINT_INTERVAL;
    function gettext_data() {
        var result=[];
        $.ajax({
            url: "/index/gaishu_data/?query=" + query,
            type: "GET",
            dataType:"json",
            success: function(data){
                // console.log(data);
                writ_text(data);
                weibo_page(data);
                 bindTabClick();
                $("#summary_tooltip").tooltip();
            }
        });       
    }
       function bindTabClick(){
        
        $("#Tablebselect").children("a").unbind();

        $("#Tableselect").children("a").click(function() {
            
            var select_a = $(this);
            var unselect_a = $(this).siblings('a');
            if(!select_a.hasClass('curr')) {
                select_a.addClass('curr');
                unselect_a.removeClass('curr');
                style = select_a.attr('value');
              
                getweibos_data(style);

            }
        });
    }

    function writ_text(data){
        var text = data;;
        var html = '';
        //data['tag']表示的是事件的标签
        html += '<h4><b>标签:'+'东盟,博览会'+'</b></h4><br/>';
        html += '<h4 style="padding-top:10px"><b>事件摘要</b></h4>';
        // html += '<span class="pull-right" style="margin: -10px auto -10px auto;">';
        // html += '<input type="checkbox" name="abs_rel_switch" checked></span>';
        $('#title_text').append(html);
        var keyhtml = '';  

        keyhtml += '<h5 style="padding-top:5px;margin-left:20px"><b>时间关键字:</b>'
        // console.log(data['key_words']);
        for(var k in data['key_words']){
            keyhtml += k+',';
        }
        keyhtml +='</h5>';        
        $('#tabkeywords').append(keyhtml);
        
        var content = '';
        var begin = new Date(parseInt(data['begin']) * 1000).toLocaleString().replace(/年|月/g, "-").replace(/日/g, " ").replace(/上午/g,'');
        var end = new Date(parseInt(data['end']) * 1000).toLocaleString().replace(/年|月/g, "-").replace(/日/g, " ").replace(/上午/g,'');
        content += ' <p style="padding-top:25px ;text-indent:2em">该事件发生于' + '<b style="background:#ACD6FF  ">'+'2013-9-2'+'</b>' + '，事件发生地点为' +'<b style="background:#ACD6FF  ">'+data['event_spot']+'</b>'  + '。' ;
        content += '该事件的舆情信息起始于' + '<b style="background:#ACD6FF  ">'+'2013-9-2'+'</b>' + '，终止于' + '<b style="background:#ACD6FF  ">'+'2013-9-6'+'</b>';
        content += '，共' +'3000' + '人参与信息发布与传播，' + '舆情信息累计' + '200'+ '条。';
        content += '参与人群集中于' + '<b style="background:#ACD6FF  ">'+'北京，上海，广州' +'</b>'+ '。';
        content += ' 前' + '<b style="background:#ACD6FF  ">'+data['k_limit']  +'</b>'+ '个关键词是：发微，领导，国家';
        // for(var k in data['key_words']){
        //     content += k+ ':' + '<b style="background:#ACD6FF  ">'+data['key_words'][k]+'</b>'+',';
        // }
        content += '。';
        content += '' + '网民情绪分布情况为：积极：0.8，愤怒：0.1，悲伤：0.1' ;
        // for(var mood in data['moodlens_pie']){
        //     // console.log(mood);
        //     if(mood== "angry"){
        //         content += '愤怒'+':' + '<b style="background:#ACD6FF  ">'+'0.1'+'</b>'+',';
        //     }
        //      if(mood = "happy"){
        //         content += '高兴'+':' + '<b style="background:#ACD6FF  ">'+'0.8'+'</b>'+',';
        //     }
        //     if(mood = 'sad'){
        //         content += '悲伤'+':' + '<b style="background:#ACD6FF  ">'+'0.1'+'</b>'+',';
        //     }
            
        // }
        content +=  '。';
        content += '代表性媒体报道如鱼骨图所示。</p>'
        $("#keywords_text").append(content);
        draw_line()
        //content += '      网民代表性观点列举如下：' + opinion
    }
    


            var happy_count = [];
            var sad_count = [];
            var angry_count = [];
            var total_count = [];
            var stramp_count = [];
            var stramp = [];
            var happy = [];
            var sad = [];
            var angry = [];


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

            var total = [];
            var total_allarea = [];
        function draw_line(){

            var emotion_type = "global";
            var names = {'happy': '高兴','angry': '愤怒','sad': '悲伤'};

            for( var time_s = 0;start_ts + time_s * during<end_ts; time_s++){
                var ts = start_ts + time_s * during ;
                var ajax_url = "/moodlens/data/?ts=" + ts + '&during=' + during + '&emotion=' + emotion_type + '&query=' + query;
                $.ajax({
                    url: ajax_url,
                    type: "GET",
                    dataType:"json",
                    async:false,
                    success: function(data){
                        // console.log(data);
                        happy = data['happy'][1]; 
                        var ns =  data['happy'][0]; 
                        // console.log(ns);                   
                        stramp =  new Date(ns).toLocaleString().replace(/年|月/g, ".").replace(/日/g, " ").replace(/上午/g, "").replace(/下午/g, "").substring(5,20);                      
                        sad = data['sad'][1];
                        angry = data['angry'][1];
                        total =  sad + angry;
                         stramp_count.push(stramp);
                         happy_count.push(happy);
                         angry_count.push(angry);
                         sad_count.push(sad);
                         total_count.push(total); 
                        // for(var name in names){
                        //     var count = data[name][1];
                        //     if(name in data){
                                
                        //         // console.log(name);
   
                        //         if(name = 'happy'){
                        //         happy_count.push(count); 
                        //          // console.log(happy_count);                              
                        //     }
                        //         if(name = 'angry'){
                        //         angry_count.push(count);
                        //     }
                        //         if(name = 'sad'){
                        //         sad_count.push(count);
                        //     }
                        //         }                           
                        // }
                    }

                });
           }
    var style;
    var style_list = [1,2,3];
   
    for( var time_s = 0;start_ts + time_s * during<end_ts; time_s++){
         var ts = start_ts + time_s * during ;
             var all = 0;
        for (var i =0; i < style_list.length; i++){
            style = style_list[i];

        $.ajax({
            url: "/propagate/total/?end_ts=" + ts + "&style=" + style +"&during="+ during + "&topic=" + topic,
            type: "GET",
            dataType:"json",
            async:false,
            success: function(data){
                console.log(data);

                folk_value = data["dcount"];
                folk = folk_value["folk"];


                media_value = data["dcount"];
                media = media_value["media"]; 
             
                opinion_leader_value = data["dcount"];
                opinion_leader = opinion_leader_value["opinion_leader"]; 
                        
                other_value = data["dcount"];
                other = other_value["other"];
            
                oversea_value = data["dcount"];
                oversea = oversea_value["oversea"]; 
                
            }
        });
        all_area = folk+media+opinion_leader+other+oversea;
        all += all_area;

        }
                total_allarea.push(all);
            
                  }
                  drawpicture(stramp_count,total_count,total_allarea);
   }
 function drawpicture(stramp_count,total_count,total_allarea){
    $('#line').highcharts({
        chart: {
            type: 'spline',
         
        },
        title: {
            text: '',
            x: -20 //center
        },
        subtitle: {
            text: '',
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
            categories: stramp_count,

                
            labels: {
                step: 24//控制多少个点显示一个
            }
          },
        yAxis: {
            title: {
                text: '条',
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
            valueSuffix: '条'
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
            name: '消极',
            data: total_count
        },{
            name: '微博总数',
            data: total_allarea
        }]
    });
}






    function weibo_page(data){          //关键微博翻页函数
        console.log(data);
        var current_data = data;
        var page_num = 10;
        if (current_data['opinion'].length) {
            if (current_data['opinion'].length < page_num) {
                page_num = current_data['opinion'].length;
                writ_opinion(current_data, 0 ,page_num);
                //create_current_table(current_data, 0, page_num);
            }
            else {
                writ_opinion(current_data, 0, page_num);
                var total_pages = 0;
                if (current_data['opinion'].length % page_num == 0) {
                    total_pages = current_data['opinion'].length / page_num;
                }
                else {
                    total_pages = current_data['opinion'].length / page_num + 1;
                }
                $('#rank_page_selection').bootpag({
                  total: total_pages,
                  page: 1,
                  maxVisible: 30
                }).on("page", function(event, num){
                  var start_row = (num - 1)* page_num;
                  var end_row = start_row + page_num;
                  if (end_row > current_data['opinion'].length)
                      end_row = current_data['opinion'].length;
                  writ_opinion(current_data, start_row, end_row);
                });
            }
        }

    } 

    function writ_opinion(data , begin, end ){

        var opinion;
        var html = "";
        html += '<div class="tang-scrollpanel-wrapper" style="height: ' + 66 * data.length  + 'px;">';
        html += '<div class="tang-scrollpanel-content">';
        html += '<ul id="weibo_ul">';

        for (var op = begin ; op <= end ; op++){             //一条条读取微博
                var sop = op.toString();

                opinion= data['opinion'][sop];
                var name = opinion['username'];
                var mid = opinion['user'];
                var ip = opinion['geo'];
                var loc = ip;
                var text = opinion['text'];
                var comments_count = opinion['comments_count'];
                // var timestamp = opinion['timestamp'];
                // console.log(timestamp);
                var timestamp = new Date(parseInt(opinion['timestamp']) * 1000).toLocaleString().replace(/年|月/g, "-").replace(/日/g, " ").replace(/上午/g,'')
                var user_link = 'http://weibo.com/u/' + mid;
                var user_image_link = opinion['profile_image_url'];
                if (user_image_link == 'unknown'){
                    user_image_link = '/static/img/unknown_profile_image.gif';
                }
                html += '<li class="item"><div class="weibo_face"><a target="_blank" href="' + user_link + '">';
                html += '<img src="' + user_image_link + '">';
                html += '</a></div>';
                html += '<div class="weibo_detail">';
                html += '<p>昵称:<a class="undlin" target="_blank" href="' + user_link  + '">' + name + '</a>&nbsp;&nbsp;UID:' + mid + '&nbsp;&nbsp;于' + ip + '&nbsp;&nbsp;发布&nbsp;&nbsp;' + text + '</p>';
                html += '<div class="weibo_info">';
                html += '<div class="weibo_pz">';
                html += '<a class="undlin" href="javascript:;" target="_blank">评论(' + comments_count + ')</a></div>';
                html += '<div class="m">';
                html += '<a class="undlin" target="_blank">' + timestamp + '</a>&nbsp;-&nbsp;';
                html += '<a target="_blank" href="http://weibo.com">新浪微博</a>&nbsp;-&nbsp;';
                html += '<a target="_blank" href="' + user_link + '">用户页面</a>';
                html += '</div>';
                html += '</div>';
                html += '</div>';
                html += '</li>';
            }            
            html += '</ul>';
            html += '</div>';
            html += '</div>';
            $("#opinion_text").empty();
            $("#opinion_text").append(html);

        }
$(function () {                                                                
    $('#column').highcharts({                                           
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
            categories: ['关注度', '爆发度', '敏感度'],
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
            valueSuffix: ' millions'                                       
        },                                                                 
        plotOptions: {                                                     
            bar: {                                                         
                dataLabels: {                                              
                    enabled: true                                          
                }                                                          
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
            name: '指标',                                             
            data: [0.3, 0.5, 0.4]                                   
        }]                                                                 
    });                                                                    
}); 
   