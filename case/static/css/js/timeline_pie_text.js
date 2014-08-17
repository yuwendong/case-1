        var timeline;
        var data;
        // Called when the Visualization API is loaded.
        $(document).ready(function(){   //网页加载时执行下面函数
        drawVisualization();
   })
        function drawVisualization() {
            // Create a JSON data table
            data = [
                {
                    'start': new Date(2014,6,26),
                    'end': new Date(2014,7,2),
                    'content': '教科书修订'
                },
                {
                    'start': new Date(2014,7,26),
                    'end': new Date(2014,8,2),
                    'content': '日本'
                },
                {
                    'start': new Date(2014,7,13,23,0,0),
                    'end': new Date(2014,7,20,10,10,0),
                    'content': '正义'
                },
                {
                    'start': new Date(2014,7,31),
                    'end': new Date(2014,8,3),
                    'content': '耻辱'
                },
                {
                    'start': new Date(2014,8,31),
                    'end': new Date(2014,9,3),
                    'content': '民族'
                },
                {
                    'start': new Date(2014,8,31),
                    'end': new Date(2014,9,3),
                    'content': '责任'
                },
                {
                    'start': new Date(2014,8,31),
                    'end': new Date(2014,9,3),
                    'content': '面对'
                },
                {
                    'start': new Date(2014,8,31),
                    'end': new Date(2014,9,3),
                    'content': '史实'
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
        var result=[];

       
        $.ajax({
            url: "/moodlens/pie/?ts=" + ts + "&query=" + query +"&during"+ during,
            type: "GET",
            dataType:"json",
            success: function(data){
                //console.log(data);
                
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
        pie_data = [{value:  result[2], name:'子类1'}, {value: result[1], name:'子类2'}, {value:  result[0], name:'子类3'}];
    
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
            data:['子类1','子类2','子类3']
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

       $(document).ready(function(){   //网页加载时执行下面函数
           getweibos_data();
        })
   function getweibos_data(){   
                var end_ts = 1378051200;
                var topic = "中国";
                var style = 2;
                var during = 900;
                var limit = 50;
                $.ajax({
                    url: "/propagate/weibos/?&topic=" + topic + "&end_ts=" + end_ts +"&limit="+limit + "&during=" + during + "&style=" + style,
                    type: "GET",
                    dataType:"json",
                    success: function(data){
                       console.log(data);
                       $("#vertical-ticker").empty();       
                        var weibo=[];
                        for (var keyword in data){
                            weibo.push(data[keyword][1]);
                            console.log(data[keyword][1]);
                        }
                        if(weibo.length > 0){
                             chg_weibos(weibo);
                        }
                        else{
                            $("#vertical-ticker").empty();
                            $("#vertical-ticker").append("关键微博为空！");
                        }
                    }
                });
            }

            function chg_weibos(data){  
                var html = "";
                var emotion_content = ['happy', 'angry', 'sad'];
                for(var i=0;i<data.length;i+=1){
                    if (data[i]['sentiment'] == 0){
                        var emotion = 'nomood'
                    }
                    else{
                        var emotion = emotion_content[data[i]['sentiment']-1];
                    }
                    var id = data[i]['_id'];
                    var user = data[i]['user'];
                    var user_link = 'http://weibo.com/u/'+data[i]['user'];
                    var text = data[i]['text'];
                    var weibo_link = data[i]['weibo_link'];
                    var comments_count = data[i]['comments_count'];
                    var geo = data[i]['geo'];
                    var retweeted_text = 'None';
                    html += "<div class=\"chartclient-annotation-letter\"><img src='/static/img/" + emotion + "_thumb.gif'></div>"
                    html +="<div class=\"chartclient-annotation-title\"><a style=\"color:#000; text-decoration:none;display:inline;\" href='" + user_link + "' target='_blank' >" + user + "</a> " +  '(' + id + ')' +"发布: ";
                    html +="<a style=\"color:#000; text-decoration:none;display:inline;\" href='" + weibo_link + "' target='_blank' >" + text + "</a></div>";
                    if(retweeted_text != 'None'){
                        html += "<div class=\"chartclient-annotation-content\">" + retweeted_text + "</div>";
                                                }
                    html += "<div class=\"chartclient-annotation-date\"><span style=\"float:right\"> 评论数：" +  comments_count + "</span></div>";
                } 
                $("#vertical-ticker").append(html);
            }