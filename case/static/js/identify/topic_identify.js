var previous_data = null;
var current_data = null;
var networkShowed = 0;
var networkUpdated = 0;
var animation = 0;
var start_ts = null;
var end_ts = null;
var sigInst = null;
var animation_timer = null;
var quota={};
var networkdata ;
var rankdata;
var node;
var y_data;


function get_network_infor(){
var  name=['number_edges', 'number_nodes','ave_degree_centrality', 'ave_degree_centrality',
 'ave_closeness_centrality','eigenvector_centrality','number_strongly_connected_components',
 'average_shortest_path_length','ave_eccentricity','power_law_distribution','ave_degree',
 'diameter','power_law_distribution','number_weakly_connected_components','degree_assortativity_coefficient','average_clustering','ave_k_core'];
var topic = "中国";
var start_ts = 1377965700;
var end_ts = 1378051200;
  for ( var key in name){
    $.ajax({
        url: "/identify/quota/?topic="+ topic +'&start_ts=' + start_ts +'&end_ts=' + end_ts +'&quota=' + name[key],
        dataType : "json",
        type : 'GET',
        async: false,
        success: function(data){

            quota[name[key]] = data;
        }

    }) ; 
  }
  var html ='';
  html += "<tr>"
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">总节点数<span class=\"tsp\">   : </span>" +quota['number_nodes'] +"</div><div class=\"lrRr\"></div></div></th>";
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">总边数<span class=\"tsp\">   : </span>" +quota['number_edges'] +"</div><div class=\"lrRr\"></div></div></th>";
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">平均节点度<span class=\"tsp\">   : </span>" +quota['ave_degree'] +"</div><div class=\"lrRr\"></div></div></th></tr>";
  html += "<tr>"
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">幂律分布系数<i id=\"power_law_distribution_tooltip\" class=\"glyphicon glyphicon-question-sign\" data-toggle=\"tooltip\" data-placement=\"right\" title=\"度分布进行幂律分布拟合得到的系数\"></i>&nbsp;&nbsp;<span class=\"tsp\">   : </span>" +quota['power_law_distribution'].toExponential(2) +"</div><div class=\"lrRr\"></div></div></th>";
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">平均度中心性<i id=\"trend_tooltip\" class=\"glyphicon glyphicon-question-sign\" data-toggle=\"tooltip\" data-placement=\"right\" title=\"单点度中心性即节点的所有连接数除以可能的最大连接数\"></i>&nbsp;&nbsp;<span class=\"tsp\">   : </span>" +quota['ave_degree_centrality'].toExponential(2) +"</div><div class=\"lrRr\"></div></div></th>";
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">平均介数中心性<i id=\"trend_tooltip\" class=\"glyphicon glyphicon-question-sign\" data-toggle=\"tooltip\" data-placement=\"right\" title=\"单点介数中心性即所有的节点对之间通过该节点的最短路径条数\"></i>&nbsp;&nbsp;<span class=\"tsp\">   : </span>" +quota['ave_degree_centrality'].toExponential(2) +"</div><div class=\"lrRr\"></div></div></th></tr>";
  html += "<tr>"
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">平均紧密中心性<i id=\"trend_tooltip\" class=\"glyphicon glyphicon-question-sign\" data-toggle=\"tooltip\" data-placement=\"right\" title=\"单点紧密中心性即节点到达它可达节点的平均距离\"></i>&nbsp;&nbsp;<span class=\"tsp\">   : </span>" +quota['ave_closeness_centrality'].toExponential(2) +"</div><div class=\"lrRr\"></div></div></th>";
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">平均特征向量中心性<i id=\"trend_tooltip\" class=\"glyphicon glyphicon-question-sign\" data-toggle=\"tooltip\" data-placement=\"right\" title=\"基于“高指数节点的连接对一个节点的贡献度比低指数节点的贡献度高”这一原则，每个节点都有一个相对指数值\"></i>&nbsp;&nbsp;<span class=\"tsp\">   : </span>" +quota['eigenvector_centrality'].toExponential(2) +"</div><div class=\"lrRr\"></div></div></th>";
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">同配性系数<i id=\"trend_tooltip\" class=\"glyphicon glyphicon-question-sign\" data-toggle=\"tooltip\" data-placement=\"right\" title=\"如果总体上度大的节点倾向于连接度大的节点，那么网络同配。同配性系数用作考察度值相近的节点是否倾向于互相连接\"></i>&nbsp;&nbsp;<span class=\"tsp\">   : </span>"+quota['degree_assortativity_coefficient'].toExponential(2)+"</div><div class=\"lrRr\"></div></div></th></tr>";
  html += "<tr>"
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">k核数<span class=\"tsp\">   : </span>"+quota['ave_k_core'].toExponential(2)+"</div><div class=\"lrRr\"></div></div></th></tr>";
  $("#mstable").append(html);

  var html1 = '';
  html1 += "<tr>"
  html1 += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">平均聚类系数<i id=\"trend_tooltip\" class=\"glyphicon glyphicon-question-sign\" data-toggle=\"tooltip\" data-placement=\"right\" title=\"单点聚类系数即某节点的邻居节点间实际存在的边数与总的可能存在的边数之比\"></i>&nbsp;&nbsp;<span class=\"tsp\">   : </span>"+quota['average_clustering'].toExponential(2)+"</div><div class=\"lrRr\"></div></div></th></tr>";
  $("#mstable1").append(html1);

  var html2 = '';
  html2 += "<tr>"
  html2 +="<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">平均最短路径长度<i id=\"trend_tooltip\" class=\"glyphicon glyphicon-question-sign\" data-toggle=\"tooltip\" data-placement=\"right\" title=\"网络中任意两节点间最短路径长度的均值\"></i>&nbsp;&nbsp;<span class=\"tsp\">   : </span>"+quota['average_shortest_path_length'].toExponential(2)+"</div><div class=\"lrRr\"></div></div></th>";
  html2 += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">直径<i id=\"trend_tooltip\" class=\"glyphicon glyphicon-question-sign\" data-toggle=\"tooltip\" data-placement=\"right\" title=\"网络中任意两个节点之间距离的最大值为网络直径\"></i>&nbsp;&nbsp;<span class=\"tsp\">   : </span>" +quota['diameter'] +"</div><div class=\"lrRr\"></div></div></th>";
  html2 +="<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">平均离心率<i id=\"trend_tooltip\" class=\"glyphicon glyphicon-question-sign\" data-toggle=\"tooltip\" data-placement=\"right\" title=\"单点偏心率计算了单点偏离中心的程度\"></i>&nbsp;&nbsp;<span class=\"tsp\">   : </span>"+quota['ave_eccentricity'].toExponential(2)+"</div><div class=\"lrRr\"></div></div></th></tr>";
  $("#mstable2").append(html2);
  //console.log(html);
}


$(document).ready(function(){
    get_network_infor();
    getnetwork_frequency();
})
// Date format
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

function draw_animation() {
    if (start_ts > end_ts) {
        if (animation_timer)
            clearInterval(animation_timer);
    }
    else {
        sigInst.iterNodes(function(n){
            var timestamp = 0;
            for (var i=0;i<n.attr['attributes'].length;i++) {
                if (n.attr['attributes'][i]['attr'] == 'timestamp')
                    timestamp = parseInt(n.attr['attributes'][i]['val']);
            }
            if (timestamp < start_ts)
                n.hidden = 0;
        }).draw(2, 2, 2);
        start_ts = start_ts + 24 * 60 * 60;
    }
}

function network_request_callback(data) {
    $("#network_progress").removeClass("active");
    $("#network_progress").removeClass("progress-striped");
    networkUpdated = 1;

    if (data) {
        $("#loading_network_data").text("计算完成!");
        $("#sigma-graph").show();
        sigInst = sigma.init($('#sigma-graph')[0]).drawingProperties({
            defaultLabelColor: '#fff'
        }).graphProperties({
            minNodeSize: 0.5,
            maxNodeSize: 5
        });

        sigInst.parseGexf(data);

        if (animation) {
            sigInst.iterNodes(function(n){
              n.hidden = 1;
              var timestamp = 0;
              for (var i=0;i<n.attr['attributes'].length;i++) {
                  if (n.attr['attributes'][i]['attr'] == 'timestamp')
                      timestamp = parseInt(n.attr['attributes'][i]['val']);
              }
              if (!start_ts)
                  start_ts = timestamp;
              else {
                  if (timestamp < start_ts)
                    start_ts = timestamp;
              }
              if (!end_ts)
                  end_ts = timestamp;
              else {
                  if (timestamp > end_ts) end_ts = timestamp;
              }
            }).draw(2,2,2);
            start_ts = end_ts - 5*24*60*60;
            setInterval(draw_animation, 1000);
        }

        (function(){
            var popUp;
            
            // This function is used to generate the attributes list from the node attributes.
            // Since the graph comes from GEXF, the attibutes look like:
            // [
            //   { attr: 'Lorem', val: '42' },
            //   { attr: 'Ipsum', val: 'dolores' },
            //   ...
            //   { attr: 'Sit',   val: 'amet' }
            // ]
            function attributesToString(attr) {
                return '<ul>' + attr.map(function(o){
                  if (o.attr == 'name'){
                    if(o.val == 'Unknown'){
                      console.log("abc");
                      return '<li>' + '博主昵称' + ' : ' + '未知' + '</li>';
                    }
                    else  
                      return '<li>' + '博主昵称' + ' : ' + o.val + '</li>';
                    }
                  else if (o.attr == 'location'){
                    if(o.val == 'Unknown'){
                      return '<li>' + '博主地域' + ' : ' + '未知' + '</li>';
                    }
                    else  
                      return '<li>' + '博主地域' + ' : ' + o.val + '</li>';

                  }
 
                  else if (o.attr == 'timestamp')
                      return '<li>' + '博主最早出现时间' + ' : ' + new Date(o.val*1000).format("yyyy-MM-dd") + '</li>';
                  else
                      return '<li>' + o.attr + ' : ' + o.val + '</li>';
                 } ).join('') +rankinfor(node)+ '</ul>';
            }
            function rankinfor(data){
              for (var i = 0 ;i< rankdata.length; i++){
                if(data['label'] == rankdata[i]['1']){
                  // console.log(rankdata[i]['0']);
                  return '<li margin-left:20px>' + '排名' + ' : ' +rankdata[i]['0'] + '</li><li><a href="http://www.weibo.com/u/'+data["label"]+'">博主链接</a></li>';
                }
                else {
                  return '<li margin-left:20px>排名 : 大于100</li><li><a target="_blank" href="http://www.weibo.com/u/'+data["label"]+'">博主链接</a></li>';
                }
              }
            }
            
            function showNodeInfo(event) {
                popUp && popUp.remove();
                
                sigInst.iterNodes(function(n){
                    node = n;
                    // console.log(node['label']);
                },[event.content[0]]);
                popUp = $(
                    '<div class="node-info-popup"></div>'
                ).append(
                    // The GEXF parser stores all the attributes in an array named
                    // 'attributes'. And since sigma.js does not recognize the key
                    // 'attributes' (unlike the keys 'label', 'color', 'size' etc),
                    // it stores it in the node 'attr' object :
                    attributesToString( node['attr']['attributes'] )
                ).css({
                    'display': 'inline-block',
                    'border-radius': 3,
                    'padding': 5,
                    'background': '#fff',
                    'color': '#000',
                    'box-shadow': '0 0 4px #666',
                    'position': 'absolute',
                    'left': node.displayX,
                    'top': node.displayY+15
                });
                
                //console.log(popUp);
                $('ul',popUp).css('margin','0 0 0 20px');
                
                $('#sigma-graph').append(popUp);
            }
             

            function waitsecond(event){
              setTimeout(function hideNodeInfo() {
                  popUp && popUp.remove();
                  popUp = false;
              }, 5000 );
            }     
            sigInst.bind('overnodes',showNodeInfo).bind('outnodes',waitsecond).draw();
        })();
    }

    else {
        //console.log('1');
        $("#loading_network_data").text("暂无结果!");
    }

}

function show_network() {
    networkShowed = 0;
    // console.log(rankdata);
    var topic = '中国'; 
    var start_ts = 1377965700;
    var end_ts = 1378051200;
  if (!networkShowed) {
            $("#network").removeClass('out');
            $("#network").addClass('in');
            networkShowed = 0;
            if (!networkUpdated){
          $.ajax({
                    url: "/identify/graph/?topic=" + topic +'&start_ts=' + start_ts +'&end_ts='+end_ts,
                    dataType: "xml",
                    type: "GET",
                    async: false,

                    success: function (data) {

                            console.log(data);
                            networkdata = data;
                            network_request_callback(data);
                    },
                    error: function(result) {
                           $("#loading_network_data").text("暂无结果!");
                          console.log("Status: " + result.status);
                  console.log("Status: " + result.textStatus);
                   console.log("Error: " + result.errorThrown); 
              }
           })
           }
   }
 else {
          networkShowed = 0;
          $("#network").removeClass('in');
           $("#network").addClass('out');
 }
}

(function ($) {
    function request_callback(data) {
    
      rankdata = data;
      // console.log(rankdata);

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
        create_current_table(current_data, 0, page_num);
    }
    else {
        create_current_table(current_data, 0, page_num);
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
      create_current_table(current_data, start_row, end_row);
        });
    }
      }
      else {
    $("#loading_current_data").text("很抱歉，本期计算结果为空!");
      }
  }
  else
      return
    }
    
    function create_current_table(data, start_row, end_row) {

      //console.log(data);<th>敏感状态</th><th><input id="select_all" type="checkbox" />全选</th>
      var cellCount = 6;
      var table = '<table class="table table-bordered">';
      var thead = '<thead><tr><th>排名</th><th style="display:none">博主ID</th><th>博主昵称</th><th>博主地域</th><th>粉丝数</th><th>关注数</th></tr></thead>';
      var tbody = '<tbody>';
      for (var i = start_row;i < end_row;i++) {
                var tr = '<tr>';
          if (data[i][3].match("海外")) {
        tr = '<tr class="success">';
          }
                for(var j = 0;j < cellCount;j++) {
        if (j == 7) {
            // checkbox
            var td = '<td><input id="uid_'+ data[i][1] + '" type="checkbox" name="now_user"></td>';
        }
        else if (j == 6) {
            // identify status
            if (data[i][j])
          var td = '<td><i class="icon-ok"></i></td>';
            else
          var td = '<td><i class="icon-remove"></i></td>';
        }
        else if(j == 0) {
            // rank status
            var td = '<td><span class="label label-important">'+data[i][j]+'</span></td>';
        }
        else if(j == 1){
            var td = '<td style="display:none">'+data[i][j]+'</td>';
        }
        else if(j == 2){
            var td = '<td><a target=\"_blank\" href=\"/profile/search/person?nickname=' + data[i][j] + '\">' + data[i][j] + '</a></td>';
        }
        else{
            var td = '<td>'+data[i][j]+'</td>';
        }
        tr += td;
                }
          tr += '</tr>';
          tbody += tr;
      }
      tbody += '</tbody>';
      table += thead + tbody;
      table += '</table>'
      $("#rank_table").html(table);
      $('#select_all').click(function(){
          var $this = $(this);
          this.checked = !this.checked;
          $.each($('#rank_table :checkbox'), function(i, val) {
        if ($(this) != $this)
            this.checked = !this.checked;
          });  
      });
    }

    function identify_request() {

      var topic = '中国'; 
      var start_ts = 1377965700;
      var end_ts = 1378051200;
      var topn = 100;

      $.get("/identify/rank/", {'topic': topic, 'start_ts': start_ts, 'end_ts': end_ts ,"topn" : topn}, request_callback, "json");
    }

    identify_request();

})(jQuery);




function getnetwork_frequency(){
var topic = "中国";
var start_ts = 1377965700;
var end_ts = 1378051200;
var index = [];
var value = [];
    $.ajax({
        url: "/identify/quota/?topic="+ topic +'&start_ts=' + start_ts +'&end_ts=' + end_ts +'&quota=degree_histogram' ,
        dataType : "json",
        type : 'GET',
        async: false,
        success: function(data){

            for (var i = 0; i< data.length; i ++){
              var s = i.toString();
              index.push(s);
              value.push(data[i]);
            }
            // console.log(index);
            // console.log(value);

           

        }
        

    }) ;

      $.ajax({
      url: "/identify/quota/?topic="+ topic +'&start_ts=' + start_ts +'&end_ts=' + end_ts +'&quota=xydict' ,
      dataType : "json",
      type : 'GET',
      async: false,
      success: function(data){
        console.log(data);
        y_data = data;

          // for (var i = 0; i< data.length; i ++){
          //   var s = i.toString();
          //   index.push(s);
          //   value.push(data[i]);
          // }
          // console.log(index);
          // console.log(value);

          // drawpicture_line(index,value);

      }
       
      

  }) ; 

  drawpicture_line(index,value,y_data);


}

function drawpicture_line(index,value,y_data) {
    $('#line').highcharts({
        title: {
            text: '',
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
            text: '',
            x: -20
        },
        xAxis: {
          title: {
            text: '节点度数'
        },
            categories:index,
          labels: {
                step: 20
            }
          },
        yAxis: {
            title: {
                text: '出现频数'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
        tooltip: {
            valueSuffix: ''
        },
            legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle',
            borderWidth: 0
        },
        series: [{
            name: '原始曲线',
            data: value
        },
        {
            name: '拟合曲线',
            data: y_data
        }]

    });
}
