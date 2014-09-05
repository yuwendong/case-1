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
        var html = "";
        html += '<div class="tang-scrollpanel-wrapper" style="height: ' + 66 * data.length  + 'px;">';
        html += '<div class="tang-scrollpanel-content">';
        html += '<ul id="weibo_ul">';

        for (var op in data['opinion']){
            opinion= data['opinion'][op];
            console.log(opinion);
                var name = opinion['username'];
                var mid = opinion['user'];
                var ip = opinion['geo'];
                var loc = ip;
                var text = opinion['text'];
                var comments_count = opinion['comments_count'];
                var timestamp = opinion['timestamp'];
                //var date = new Date(timestamp * 1000).format("yyyy年MM月dd日 hh:mm:ss");
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

            // var user = opinion['user'];
            // var text = opinion['text'];
            // var reposts_count = opinion['reposts_count'];
            // var timestamp = opinion['timestamp'];
            // var date = new Date(parseInt(timestamp) * 1000).toLocaleString().replace(/年|月/g, "-").replace(/日/g, " ").replace(/上午/g,'');
            // html1 += '<li class="item">';
       
            // html1 += '<p5 padding-left:15px;text-decoration: none;>用户id:' + '<b style="background:#ACD6FF  ">'+user +'</b>' + '&nbsp;&nbsp;发布&nbsp;&nbsp;' + text + " "+ "发布时间"+'<a class="undlin" target="_blank">'+date + '</a>&nbsp;&nbsp;'+'</p5>';
            // html1 += '<div class="weibo_info">';
            
           

          
            // html1 += '</div>';
            // html1 += '</li>';
            $("#opinion_text").append(html);

        }
 
   