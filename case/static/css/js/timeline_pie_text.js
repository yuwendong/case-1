
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
        // var data;
        // Called when the Visualization API is loaded.
    $(document).ready(function(){   //网页加载时执行下面函数
        gettimeline_data();
        console.log('abc');

    })
    var result = [];
    var result1 = [];
    var result2 = [];
    var result3 = [];
    var topic = '东盟,博览会';

    function gettimeline_data() {
        var html ="<table>";
        $.ajax({
            url: "/opinion/time/?topic=" + topic,
            type: "GET",
            dataType:"json",
            async: false,
            success: function(data){

               var n = data.length;
               var si = 100.0/n;
               var si_str = si + '%';
               for (var i = 0;i < data.length;i++) {
                    result[i] = data[i][1];
                    result1[i] = data[i][2];
                    result2[i] = data[i][0]; 

                    var s = i.toString();
                    if(i==0){
                        html += '<tr><td style="width:'+si_str+'"><a topic='+ result2[i] + ' name="c_topic" class="tabLi gColor0 curr" href="javascript:;" style="display: block;">';
                        html += '<div class="nmTab">'+ result2[i]+ '</div>';
                        html += '<div class="hvTab">'+result2[i]+'</div></a></td>';
                    }
                    else{
                        html += '<td style="width:'+si_str+'"><a topic='+ result2[i] + ' name="c_topic" class="tabLi gColor0" href="javascript:;" style="display: block;">';
                        html += '<div class="nmTab">'+ result2[i]+ '</div>';
                        html += '<div class="hvTab">'+result2[i]+'</div></a></td>';
                    }
                };
                html += '</tr></table>';
                $("#Tableselect").append(html);
                bindSentimentTabClick();

               drawVisualization(); 
               getkeywords_data();
               getweibos_data(result2[1]);
                             
            }

       
        });

    }



    function bindSentimentTabClick(){
        
        /*$("#Tablebselect").children("a").unbind();
        console.log('yuan');
        console.log($("#Tablebselect").children("a"));*/

        $("[name='c_topic']").click(function() {
            
            var select_a = $(this);
            var unselect_a = $("[name='c_topic']");//$(this).siblings('a');
            if(!select_a.hasClass('curr')) {
                select_a.addClass('curr');
                unselect_a.removeClass('curr');
                style = select_a.attr('topic');
              
                getweibos_data(style);

            }
        });
    }


        function drawVisualization() {
            var data = [];
            var data_start = [];
            var data_end = [];
            for (var i =0 ; i< result.length; i++){
                data_end[i] = new Date(parseInt(result1[i]) * 1000);
                data_start[i] = new Date(parseInt(result[i]) * 1000);
                data[i] = {'start':data_start[i],'end':data_end[i],'content':result2[i]};
              
            }
						var height_str = 40*result2.length;
						height_str += 'px'; 
            

            // specify options
            var options = {
                'width':  '100%',
                'height': height_str,
                'editable': true,   // enable dragging and editing events
                'style': 'box'
            };

            // Instantiate our timeline object.
            timeline = new links.Timeline(document.getElementById('mytimeline'));
            // Draw our timeline with the created data and options

            timeline.draw(data, options);



            

        }




    $(document).ready(function(){   //网页加载时执行下面函数
       getpie_data();
   })

    function getpie_data() {
        var result = [];
        $.ajax({
            url: "/opinion/ratio/?topic=" + topic,
            type: "GET",
            dataType:"json",
            async:false,
            success: function(data){
            	for (var i =0 ; i< result2.length; i++){
            		result3[i] = data[result2[i]]
            	}

                on_update(result);
            }
        });
       
    }

    function on_update(result) {


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

    function getweibos_data(data){   
            var topic_child = data;
            var dataselect = [];
            $.ajax({
                url: "/opinion/weibos/?&topic=" + topic,
                type: "GET",
                dataType:"json",
                success: function(data){
                    
                    for (var i = 0 ;i< data[topic_child].length; i++){
                         dataselect.push(data[topic_child][i]);
                    }
                console.log(dataselect);
                chg_weibos(dataselect);
            }
        });
    }


            function chg_weibos(data){  
                $("#vertical-ticker").empty();
                console.log(data);
                var html = "";
                var temporary
                var data_af = [];
                var time;
                // for (var j =0 ; j < data.length; j++){
                //     rank_count.push(data[j]['reposts_count']);
                // }
                // rank_count_af = rank_count.sort(function(a,b){return b-a});
                
                // for (var m = 0; m < rank_count_af.length; m++){
                //     time = 0;
                //     for (var k = 0; k < data.length; k++){
                //         if(data[k]['reposts_count'] == rank_count_af[m]){ 
                //             time++;                           
                //             if(time == 1){
                //                 date_af.push(data[k]);
                //             }
                                                                                          
                //         }
                //     }
                // }
               /* for(var m = 0; m< data.length; m++){
                    for(var n = m+1; n< data.length; n++){
                        if(data[m]['reposts_count'] < data[n]['reposts_count']){
                            temporary = data[n];
                            data[n] = data[m];
                            data[m] = temporary;

                        }
                    }
                }*/
                
                html += '<div class="tang-scrollpanel-wrapper" style="height: ' + 66 * data.length  + 'px;">';
                html += '<div class="tang-scrollpanel-content">';
                html += '<ul id="weibo_ul">';
                for(var i = 0; i < data.length; i += 1){
                    console.log(data);
                var da = data[i];
                var uid = da['user'];
                /*var name;
                if ('name' in da){
                    name = da['name'];
                    if(name == 'unknown'){
                        name = '未知';
                    }
                }
                else{
                    name = '未知';
                }*/
                var mid = da['_id'];
                var text = da['text'];
                var reposts_count = da['reposts_count'];
                var comments_count = da['comments_count'];
                var timestamp = da['time'];
                var date = new Date(timestamp * 1000).format("yyyy年MM月dd日 hh:mm:ss");
                var user_link = 'http://weibo.com/u/' + uid;
                var user_image_link = '/static/img/unknown_profile_image.gif';
                
                html += '<li class="item"><div class="weibo_face"><a target="_blank" href="' + user_link + '">';
                html += '<img src="' + user_image_link + '">';
                html += '</a></div>';
                html += '<div class="weibo_detail">';
                html += '<p>昵称:<a class="undlin" target="_blank" href="' + user_link  + '">' + uid + '</a>&nbsp;&nbsp;发布&nbsp;&nbsp;' + text + '</p>';
                html += '<div class="weibo_info">';
                html += '<div class="weibo_pz">';
                html += '<a class="undlin" href="javascript:;" target="_blank">转发(' + reposts_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
                html += '<a class="undlin" href="javascript:;" target="_blank">评论(' + comments_count + ')</a></div>';
                html += '<div class="m">';
                html += '<a class="undlin">' + date + '</a>&nbsp;-&nbsp;';
                html += '<a target="_blank" href="http://weibo.com">新浪微博</a>&nbsp;-&nbsp;';
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
                $.ajax({
                    url: "/opinion/keywords/?&topic=" + topic,
                    type: "GET",
                    dataType:"json",
                    success: function(data){
                        console.log(data);                            
                        drawtable(data);
                    }
                });
            }

        function drawtable(data){
            /*var topic_child = {};
            var html = '';
            for(var key in data){
                topic_child[key] = [];
                for (var i = 0 ; i < data[key].length; i++){
                    topic_child[key].push(data[key][i][0]);
                }
            }
            console.log("123");
            console.log(topic_child);
            for(var topic in topic_child){
                console.log(topic);
                console.log(result2[0]);
                if (topic == result2[0]){
                    html += '<tr topic='+topic+' class="tablecurrent">'; 
                }
                else{
                    html += '<tr topic='+topic+'>'; 
                }
                html += "<td><b>"+m+"</b></td><td><b onclick = \"connect('"+topic+"')\" style =\"width:20px\">"+topic+"</b></td>";
                
                if(topic_child[topic].length > 5){
                    for(var j = 0; j < 5; j++){
                        html += '<td>'+topic_child[topic][j]+'</td>';
                    }
                }
                
                else{
                    for(var m = 0;m < topic_child[topic].length; m++){
                        html += '<td>'+topic_child[topic][m]+'</td>';
                    }
                }

            }

            $("#alternatecolor").append(html);
                 // $("#alternate").append(html1);*/
            		var topic_child_keywords = {};
                var html = '';
                var target_html = '';
                var m = 0;
                var number;               
                for (var key in data){
                    topic_child_keywords[key] = [];
                    for (var i = 0; i < data[key].length; i++){
                        topic_child_keywords[key].push(data[key][i][0]);
                    }
                }
                for (var topic in topic_child_keywords){
                	
                    m++;
                    if( m > 10) {break;}
                    if (topic == result2[0]){
                    	html += '<tr topic='+topic+' class="tablecurrent" style="height:25px">'; 
                		}
                		else{
                    	html += '<tr topic='+topic+'>'; 
                		}                  
                    html += "<td><b>"+m+"</b></td><td><b onclick = \"connect('"+topic+"')\" style =\"width:20px\">"+topic+"</b></td>";
                    if (topic_child_keywords[topic].length>=5){
                    	total = 5;
                    }
                    else{
                    	total = topic_child_keywords[topic].length;
                    }
                    for (var n = 0 ;n < total; n++){
                        html += '<td>'+topic_child_keywords[topic][n]+'</td>'
                    }
                    html += "</tr>";
                }
                
                $("#alternatecolor").append(html);
                
                for (var topic in topic_child_keywords){
                    target_html += '<tr style="height:25px">';                    
                    target_html += '<td><b style =\"width:20px\">'+topic+'</b></td>';
                    if (topic_child_keywords[topic].length>=10){
                    	total = 10;
                    }
                    else{
                    	total = topic_child_keywords[topic].length;
                    }
                    for (var n = 0 ;n < total; n++){
                        target_html += '<td>'+topic_child_keywords[topic][n]+'</td>'
                    }
                    target_html += "</tr>";
                }
                
                $("#alternate").append(target_html);
        }
       
        function connect(data){
            var value_data = data;
            console.log(data);

            $("#alternatecolor tr").each(function() {
                var select_all =$(this);
                if(select_all.attr('topic') == value_data){
                    if(!select_all.hasClass("tablecurrent")){
                        select_all.addClass("tablecurrent");
                    }
                }
                else{
                    if(select_all.hasClass("tablecurrent")){
                        select_all.removeClass('tablecurrent');
                    }
                }

            })
            refreshWeiboTab(value_data);
        }

        function refreshWeiboTab(data){
            var curr_data = data;
             $("#Tableselect a").each(function() {
                var select_a = $(this);
                var select_a_sentiment = select_a.attr('topic');
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
             console.log("curr"+curr_data);
            getweibos_data(curr_data);
        }