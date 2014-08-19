        var timeline;
        var data;
        // Called when the Visualization API is loaded.
        $(document).ready(function(){   //网页加载时执行下面函数
        gettimeline_data();
   })
        var result = [];
        var result1 = [];
        var result2 = [];

    function gettimeline_data() {
        var topic = '博鳌';
        $.ajax({
            url: "/opinion/time/?topic=" + topic,
            type: "GET",
            dataType:"json",
            success: function(data){
                console.log(data);

               for (var i = 0;i < data.length;i++) {
                    result[i] = data[i][i][0];
                };
                for (var i = 0;i < data.length;i++) {
                    result1[i] = data[i][i][1]; 
                };
                for (var i = 0;i < data.length;i++) {
                    result2[i] = data[i][i][2][1]; 
                };
               drawVisualization(); 
                
              console.log(result);
              console.log(result1);
              console.log(result2);
            
                

                //console.log(data['happy']);
      
                // result[1]=data["sad"];
                // result[2]=data["angry"];

                // on_update(result);

            }

       
    });

}

        function drawVisualization() {
            // Create a JSON data table
             console.log(result2[0]); 
             ns_start = [];
             ns_end = [];
            for (var i = 0; i < result.length; i++){

            ns_start[i] = new Date(parseInt(result[i]) * 1000).toLocaleString();
        }

            for (var i = 0; i < result1.length; i++){

            ns_end[i] = new Date(parseInt(result1[i]) * 1000).toLocaleString();
        }
       console.log(ns_start);
       console.log(ns_end);
            data = [
                {
                    'start': new Date(2014,6,26),
                    'end': new Date(2014,7,2),
                    'content': result2[0]
                },
                {
                    'start': new Date(2014,7,26),
                    'end': new Date(2014,8,2),
                    'content': result2[1]
                },
                {
                    'start': new Date(2014,7,13,23,0,0),
                    'end': new Date(2014,7,20,10,10,0),
                    'content': result2[2]
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
            success: function(data){
                console.log(data);
              //   for (var i = 0;i < data.length;i++) {
              //       result[i] = data[i][0];
              //   };
                
              // console.log(result);

                

                //console.log(data['happy']);
      
                // result[1]=data["sad"];
                // result[2]=data["angry"];

                // on_update(result);
            }
        });
       
    }

    // function on_update(result) {
    // //alert('on_update' + result[0]);
    // //alert('on_update' + result[1]);
    // //alert('on_update' + result[2]);
    //     //result1=getpie_data();

    //     var pie_data=[];
    //     pie_data = [{value:  result[2], name:'子类1'}, {value: result[1], name:'子类2'}, {value:  result[0], name:'子类3'}];
    
    // option = {
    //     title : {
    //         text: '子类占比图',
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
    //     legend: {
    //         orient:'vertical',
    //         x : 'left',
    //         data:['子话题1','子类2','子类3']
    //     },
    //     toolbox: {
    //     show : true,
    //     feature : {
    //       mark : {show: true},
    //        dataView : {show: true, readOnly: false},
    //         restore : {show: true},
            
    //         saveAsImage : {show: true}
    //     }
    // },
    //     calculable : true,
    //     series : [
    //         {
    //             name:'访问来源',
    //             type:'pie',
    //             radius : '50%',
    //             center: ['50%', '60%'],
    //             data: pie_data
    //         }
    //     ]
    // };
    // var myChart = echarts.init(document.getElementById('main'));
    // myChart.setOption(option);
        
    // }

       $(document).ready(function(){   //网页加载时执行下面函数
           getweibos_data();
        })
   function getweibos_data(){   
                var topic = '博鳌';
                $.ajax({
                    url: "/opinion/weibos/?&topic=" + topic,
                    type: "GET",
                    dataType:"json",
                    success: function(data){
                       console.log(data);
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
                       //  }
                    }
                });
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