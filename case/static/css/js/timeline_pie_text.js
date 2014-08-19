    Date.prototype.format = function(format) { 
        var o = { 
        "M+" : this.getMonth()+1, //month 
        "d+" : this.getDate(),    //day 
        "h+" : this.getHours(),   //hour 
        "m+" : this.getMinutes(), //minute 
        "s+" : this.getSeconds(), //second 
        "q+" : Math.floor((this.getMonth()+3)/3),  //quarter 
        "S" : this.getMilliseconds() //millisecond 
        } 
        if(/(y+)/.test(format)) 
        format=format.replace(RegExp.$1, (this.getFullYear()+"").substr(4 - RegExp.$1.length)); 
        for(var k in o)
        if(new RegExp("("+ k +")").test(format)) 
            format = format.replace(RegExp.$1, RegExp.$1.length==1 ? o[k] : ("00"+ o[k]).substr((""+ o[k]).length)); 
        return format; 
    }

    var timeline;
        var data;
        // Called when the Visualization API is loaded.
        $(document).ready(function(){   //网页加载时执行下面函数

        var style = '0';
        gettimeline_data();
        getweibos_data(style);
   })
        var result = [];
        var result1 = [];
        var result2 = [];

    function gettimeline_data() {
        var topic = '博鳌';
        var html ="";
        $.ajax({
            url: "/opinion/time/?topic=" + topic,
            type: "GET",
            dataType:"json",
            async: false,
            success: function(data){
               

               for (var i = 0;i < data.length;i++) {
                    result[i] = data[i][i][0];
                };
                for (var i = 0;i < data.length;i++) {
                    result1[i] = data[i][i][1]; 
                };
                for (var i = 0;i < data.length;i++) {
<<<<<<< HEAD
                    result2[i] = data[i][i][2][0]+'-'+data[i][i][2][1]; 

                    var s = i.toString();
                    if(i==0){
                        html += '<a value='+ s + ' class="tabLi gColor0 curr" href="javascript:;" style="display: block;">';
                        html += '<div class="nmTab">'+ result2[i]+ '</div>';
                        html += '<div class="hvTab">'+result2[i]+'</div></a>';
                    }
                    else{
                        html += '<a value='+ s + ' class="tabLi gColor0" href="javascript:;" style="display: block;">';
                        html += '<div class="nmTab">'+ result2[i]+ '</div>';
                        html += '<div class="hvTab">'+result2[i]+'</div></a>';
                    }
                    
                };
                $("#Tableselect").append(html);
                bindSentimentTabClick();

               drawVisualization(); 
               getkeywords_data();
                             
            }

       
    });

}



    function bindSentimentTabClick(){
        
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


        function drawVisualization() {
            var data = [];
            var data1 = [];
            for (var i =0 ; i< result.length; i++){
                data1[i] = new Date(parseInt(result1[i]) * 1000);
                data[i] = new Date(parseInt(result[i]) * 1000);
            }

            data = [
                {
                    'start': data[0],
                    'end': data1[0],
                    'content': result2[0]
                },
                {
                    'start': data[1],
                    'end': data1[1],
                    'content': result2[1]
                },
                {
                    'start': data[2],
                    'end': data1[2],
                    'content': result2[2]
                },
                {
                    'start': data[3],
                    'end': data1[3],
                    'content': result2[3]
                },
                {
                    'start': data[4],
                    'end': data1[4],
                    'content': result2[4]
                },
                {
                    'start': data[5],
                    'end': data1[5],
                    'content': result2[5]
                },
                {
                    'start': data[6],
                    'end': data1[6],
                    'content': result2[6]
                },
                {
                    'start': data[7],
                    'end': data1[7],
                    'content': result2[7]
                },
                {
                    'start': data[8],
                    'end': data1[8],
                    'content': result2[8]
                },
                {
                    'start': data[9],
                    'end': data1[9],
                    'content': result2[9]
                },                
                {
                    'start': data[10],
                    'end': data1[10],
                    'content': result2[10]
                }
                // {
                //     'start': ns_start[3],
                //     'end': ns_end[3],
                //     'content': result2[3]
                // },
                // {
                //     'start': ns_start[4],
                //     'end': ns_end[4],
                //     'content': result2[4]
                // },
                // {
                //     'start': ns_start[5],
                //     'end': ns_end[5],
                //     'content': result2[5]
                // },
                // {
                //     'start': ns_start[6],
                //     'end': ns_end[6],
                //     'content': result2[6]
                // },
                // {
                //     'start': ns_start[7],
                //     'end': ns_end[7],
                //     'content': result2[7]
                // },
                // {
                //     'start': ns_start[8],
                //     'end': ns_end[8],
                //     'content': result2[8]
                // },
                // {
                //     'start': ns_start[9],
                //     'end': ns_end[9],
                //     'content': result2[9]
                // },
                // {
                //     'start': ns_start[10],
                //     'end': ns_end[10],
                //     'content': result2[10]
                // }
            ];

            // specify options
            var options = {
                'width':  '100%',
                'height': '300px',
                'editable': true,   // enable dragging and editing events
                'style': 'box'
            };

            // Instantiate our timeline object.
            timeline = new links.Timeline(document.getElementById('mytimeline'));

            // Draw our timeline with the created data and options
            timeline.draw(data, options);
        }
    var result1=[];
    var query = "中国";
    var ts = 1378035900;
    var START_TS = 1377965700
    var during = ts-START_TS;


    $(document).ready(function(){   //网页加载时执行下面函数
       getpie_data();
   })

    function getpie_data() {
        var result = [];
        var topic = '博鳌';
        $.ajax({
            url: "/opinion/ratio/?topic=" + topic,
            type: "GET",
            dataType:"json",
            async:false,
            success: function(data){
                
                result[0]=data['10'][0];
                result[1]=data['0'][1];
                result[10]=data['1'][10];
                result[3]=data['2'][3];
                result[2]=data['3'][2];
                result[5]=data['4'][5];
                result[4]=data['5'][4];
                result[7]=data['6'][7];
                result[6]=data['7'][6];
                result[9]=data['8'][9];
                result[8]=data['9'][8];
                 on_update(result);
            }
        });
       
    }

    function on_update(result) {
        console.log(result2);

      var pie_data=[];
        pie_data = [{value:  result[0], name:result2[0]}, {value: result[1], name:result2[1]}, 
        {value:  result[2], name:result2[2]}, {value: result[3], name:result2[3]},
         {value:  result[4], name:result2[4]},{value:  result[5], name:result2[5]},{value:  result[6], name:result2[6]}
         ,{value:  result[7], name:result2[7]},{value:  result[8], name:result2[8]},{value:  result[9], name:result2[9]},
         {value:  result[10], name:result2[10]}];
    
    option = {
        title : {
            text: '子类占比图',
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
            data:result2//['子类0','子类1','子类2','子类3','子类4','子类5','子类6','子类7','子类8','子类9','子类10']
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
     var myChart = echarts.init(document.getElementById('main'));
     myChart.setOption(option);
        
    }
    
    // $(document).ready(function(){   //网页加载时执行下面函数
    //     var style = '1';
    //    keyword_data();
    //    switch_curr_add();
    //    getpie_data();
    //    getweibos_data(style);
    //    bindSentimentTabClick();
    // })

    // function bindSentimentTabClick(){
        
    //     $("#Tablebselect").children("a").unbind();

    //     $("#Tableselect").children("a").click(function() {
    //         console.log("avvv");
    //         var select_a = $(this);
    //         var unselect_a = $(this).siblings('a');
    //         if(!select_a.hasClass('curr')) {
    //             select_a.addClass('curr');
    //             unselect_a.removeClass('curr');
    //             style = select_a.attr('value');
    //             getweibos_data(style);
    //         }
    //     });
    // }

        function getweibos_data(style){   
                var topic = '博鳌';
                var selects = style;
                //console.log(selects);
                var dataselect = [];
                $.ajax({
                    url: "/opinion/weibos/?&topic=" + topic,
                    type: "GET",
                    dataType:"json",
                    success: function(data){
                        

                        for (var i = 0 ;i< data[selects][selects].length; i++){
                             var s = i.toString();
                             dataselect.push(data[selects][selects][s]['0'])

                        }
                      
                        chg_weibos(dataselect);
                       // $("#vertical-ticker").empty();       
                       //  var weibo=[];
                       //  for (var keyword in data){
                       //      weibo.push(data[keyword][1]);
                       //      console.log(data[keyword][1]);
                       //  }
                       //  if(weibo.length > 0){
                       //       chg_weibos(weibo);
                       //  }
                       //  else{
                       //      $("#vertical-ticker").empty();
                       //      $("#vertical-ticker").append("关键微博为空！");
                    }
        });
    }


            function chg_weibos(data){  
                $("#vertical-ticker").empty();
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
            $("#vertical-ticker").append(html);
            }
 



        function getkeywords_data(){   
                var topic = '博鳌';
                $.ajax({
                    url: "/opinion/keywords/?&topic=" + topic,
                    type: "GET",
                    dataType:"json",
                    success: function(data){
                           //console.log(data);
                            drawtable(data);
                    }
                });
            }

        function drawtable(data){
            
            var tagout ;
            var tagin;
            var html = '';
            for (var i =0 ;i<data.length; i++){
                var html = '';
                var keyword = [];
                var s = i.toString();
                tagout = data[s];
                 for (var k in tagout){
                    tagin = k;
                 }
                 for (var k1 in tagout[tagin]){
                    keyword.push(tagout[tagin][k1]['0']);
                    //console.log(tagout[tagin][k1]['0']);
                }
                var tindex = Number(tagin);
                html += '<tr>';
                html += '<td><b>'+result2[tindex]+'</b></td><td>'+keyword[0]+'</td><td>'+keyword[1]+'</td><td>'+keyword[2]+'</td><td>'+keyword[3]+'</td><td>'+keyword[4]+'</td>';
                html += '</tr>';
                //console.log(keyword);
                 //console.log(tagin);
                 //console.log(html);
                 $("#alternatecolor").append(html);
            }
           
           
        }
            // function chg_weibos(data){  
            //     var html = "";
            //     var emotion_content = ['happy', 'angry', 'sad'];
            //     for(var i=0;i<data.length;i+=1){
            //         if (data[i]['sentiment'] == 0){
            //             var emotion = 'nomood'
            //         }
            //         else{
            //             var emotion = emotion_content[data[i]['sentiment']-1];
            //         }
            //         var id = data[i]['_id'];
            //         var user = data[i]['user'];
            //         var user_link = 'http://weibo.com/u/'+data[i]['user'];
            //         var text = data[i]['text'];
            //         var weibo_link = data[i]['weibo_link'];
            //         var comments_count = data[i]['comments_count'];
            //         var geo = data[i]['geo'];
            //         var retweeted_text = 'None';
            //         html += "<div class=\"chartclient-annotation-letter\"><img src='/static/img/" + emotion + "_thumb.gif'></div>"
            //         html +="<div class=\"chartclient-annotation-title\"><a style=\"color:#000; text-decoration:none;display:inline;\" href='" + user_link + "' target='_blank' >" + user + "</a> " +  '(' + id + ')' +"发布: ";
            //         html +="<a style=\"color:#000; text-decoration:none;display:inline;\" href='" + weibo_link + "' target='_blank' >" + text + "</a></div>";
            //         if(retweeted_text != 'None'){
            //             html += "<div class=\"chartclient-annotation-content\">" + retweeted_text + "</div>";
            //                                     }
            //         html += "<div class=\"chartclient-annotation-date\"><span style=\"float:right\"> 评论数：" +  comments_count + "</span></div>";
            //     } 
            //     $("#vertical-ticker").append(html);
            // }
