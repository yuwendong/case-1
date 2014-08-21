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
               console.log(data);
               for (var i = 0;i < data.length;i++) {
                    result[i] = data[i][i][0];
                };
                for (var i = 0;i < data.length;i++) {
                    result1[i] = data[i][i][1]; 
                };
                console.log(result1);
                for (var i = 0;i < data.length;i++) {
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
                    'content': result2[0],
                    'link': "www.baidu.com"
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
                    'content': result2[10],
                }
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
            console.log(timeline);


            

        }

    var query = "中国";
    var ts = 1378035900;
    var START_TS = 1377965700
    var during = ts-START_TS;
    var result3 = [];


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
                result3[0]=data['10']['10'];
                result3[1]=data['0']['0'];
                result3[10]=data['1']['1'];
                result3[3]=data['2']['2'];
                result3[2]=data['3']['3'];
                result3[5]=data['4']['4'];
                result3[4]=data['5']['5'];
                result3[7]=data['6']['6'];
                result3[6]=data['7']['7'];
                result3[9]=data['8']['8'];
                result3[8]=data['9']['9'];

                on_update(result);
            }
        });
       
    }

    function on_update(result) {

console.log(result3);
        var percentage = []; 
        percentage[0] = (result3[0]*100).toFixed(2)+"%";
        percentage[1] = (result3[1]*100).toFixed(2)+"%";
        percentage[2] = (result3[2]*100).toFixed(2)+"%";
        percentage[3] = (result3[3]*100).toFixed(2)+"%";
        percentage[4] = (result3[4]*100).toFixed(2)+"%";
        percentage[5] = (result3[5]*100).toFixed(2)+"%";
        percentage[6] = (result3[6]*100).toFixed(2)+"%";
        percentage[7] = (result3[7]*100).toFixed(2)+"%";
        percentage[8] = (result3[8]*100).toFixed(2)+"%";
        percentage[9] = (result3[9]*100).toFixed(2)+"%";
        percentage[10] = (result3[10]*100).toFixed(2)+"%";
 

      var pie_data=[];
        pie_data = [{value:  result3[0], name:result2[0]+percentage[0]}, {value: result3[1], name:result2[1]+percentage[1]}, 
        {value:  result3[2], name:result2[2]+percentage[2]}, {value: result3[3], name:result2[3]+percentage[3]},
         {value:  result3[4], name:result2[4]+percentage[4]},{value:  result3[5], name:result2[5]+percentage[5]},{value:  result[6], name:result2[6]+percentage[6]}
         ,{value:  result3[7], name:result2[7]+percentage[7]},{value:  result3[8], name:result2[8]+percentage[8]},{value:  result3[9], name:result2[9]+percentage[9]},
         {value:  result3[10], name:result2[10]+percentage[10]}];
    
    option = {
        title : {
            text: '',
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
                var m = i+1;
                var keyword = [];
                var s = i.toString();
                tagout = data[s];
                 for (var k in tagout){
                    tagin = k;
                 }
                for (var k1 in tagout[tagin]){
                    if(tagout[tagin][k1]['0'] ==null || tagout[tagin][k1]['0'] == undefined ){
                        tagout[tagin][k1]['0'] =='';
                        console.log("abc");
                    }
                    keyword.push(tagout[tagin][k1]['0']);
                    console.log(tagout[tagin][k1]['0']);
                }
                var tindex = Number(tagin);
                console.log(keyword);
                console.log(tagin);
                html += '<tr>';
                html += '<td><b>'+m+'</b></td><td><b onclick = \"connect('+tagin+')\" style =\"width:20px\">'+result2[tindex]+'</b></td><td>'+keyword[0]+'</td><td>'+keyword[1]+'</td><td>'+keyword[2]+'</td><td>'+keyword[3]+'</td><td>'+keyword[4]+'</td>';
                html += '</tr>';
                //console.log(keyword);
                 //console.log(tagin);
                 //console.log(html);
                 $("#alternatecolor").append(html);
            }
           
           
        }
        function connect(data){
            var value_data = data;
            refreshWeiboTab(value_data);
        }

        function refreshWeiboTab(data){
            var curr_data = data;
             $("#Tableselect a").each(function() {
                var select_a = $(this);
                console.log(select_a.attr('value'));
                var select_a_sentiment = select_a.attr('value');
                if (select_a_sentiment == curr_data){
                    if(!select_a.hasClass('curr')) {
                        select_a.addClass('curr');
                    }
                }
                else{
                    if(select_a.hasClass('curr')) {
                        select_a.removeClass('curr');
                    }
                }
            });
            getweibos_data(curr_data);
        }