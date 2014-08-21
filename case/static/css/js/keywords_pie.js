$(document).ready(function(){   //网页加载时执行下面函数
           gettext_data();
        })
    var query = "中国";
    function gettext_data() {
        var result=[];
        $.ajax({
            url: "/index/gaishu_data/?query=" + query,
            type: "GET",
            dataType:"json",
            success: function(data){
                console.log(data);
                writ_text(data);
                writ_opinion(data);
                $("#summary_tooltip").tooltip();
            }
        });       
    }

    function writ_text(data){
        var text = data;
        var html = '';

        html += '<h4><b>标签:'+data['tag']+'</b></h4>';
        html +=  '<i id="summary_tooltip" class="glyphicon glyphicon-question-sign" data-toggle="tooltip" data-placement="right" title="事件总体概述"></i>&nbsp;&nbsp';      
        html += '<span class="pull-right" style="margin: -10px auto -10px auto;">';
        html += '<input type="checkbox" name="abs_rel_switch" checked></span>';
        $('#title_text').append(html);
        
        var content = '';
        var begin = new Date(parseInt(data['begin']) * 1000).toLocaleString().replace(/年|月/g, "-").replace(/日/g, " ").replace(/上午/g,'');
        var end = new Date(parseInt(data['end']) * 1000).toLocaleString().replace(/年|月/g, "-").replace(/日/g, " ").replace(/上午/g,'');
        content += ' <p> 九一八发生于' + '<b style="background:#ACD6FF  ">'+data['event_time']+'</b>' + '，事件发生地点为' +'<b style="background:#ACD6FF  ">'+data['event_spot']+'</b>'  + '。' + '<b style="background:#ACD6FF  ">'+data['event_summary']+'</b>';
        content += '该事件的舆情信息起始于' + '<b style="background:#ACD6FF  ">'+begin+'</b>' + '，终止于' + '<b style="background:#ACD6FF  ">'+end+'</b>';
        content += '，共' +data['user_count'] + '人参与信息发布与传播，' + '舆情信息累计' + data['count']+ '条。';
        content += '参与人群集中于' + '<b style="background:#ACD6FF  ">'+data['area'] +'</b>'+ '。';
        content += ' 前' + '<b style="background:#ACD6FF  ">'+data['k_limit']  +'</b>'+ '个关键词是：';
        for(var k in data['key_words']){
            content += k+ ':' + '<b style="background:#ACD6FF  ">'+data['key_words'][k]+'</b>'+',';
        }
        content += '。';
        content += '' + '网民情绪分布情况为：' ;
        for(var mood in data['moodlens_pie']){
            console.log(mood);
            content += mood+':' + '<b style="background:#ACD6FF  ">'+data['moodlens_pie'][mood]+'</b>'+',';
        }
        content +=  '。';
        content += '代表性媒体报道如鱼骨图所示。</p>'
        console.log(content);
        $("#keywords_text").append(content);
        //content += '      网民代表性观点列举如下：' + opinion
    } 

    function writ_opinion(data){
        var opinion;

        for (var op in data['opinion']){
            console.log(op);
            var html1 = '';
            opinion= data['opinion'][op];
            console.log(opinion);
            var user = opinion['user'];
            var text = opinion['text'];
            var reposts_count = opinion['reposts_count'];
            var timestamp = opinion['timestamp'];
            var date = new Date(parseInt(timestamp) * 1000).toLocaleString().replace(/年|月/g, "-").replace(/日/g, " ").replace(/上午/g,'');
            html1 += '<li class="item">';
       
            html1 += '<p5 padding-left:15px;text-decoration: none;>用户id:' + '<b style="background:#ACD6FF  ">'+user +'</b>' + '&nbsp;&nbsp;发布&nbsp;&nbsp;' + text + " "+ "发布时间"+'<a class="undlin" target="_blank">'+date + '</a>&nbsp;&nbsp;'+'</p5>';
            html1 += '<div class="weibo_info">';
            
           

          
            html1 += '</div>';
            html1 += '</li>';
            $("#opinion_text").append(html1);

        }
    }
   