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
var topic = QUERY; 
var curr = {};
var index_time = [];
$(document).ready(function(){
    getindex_data();

 })
 function getindex_data(){
        $.ajax({
        url:"/quota_system/topic/?topic="+topic,
        dataType: "json",
        type: "GET",
        async:false,
        success :function(data){            
            console.log(data);
           
             exp_data(data);       
        }       
    });
}
function exp_data(data){
  var index = data["index_evolution"];
  var quota = data['f_quota_evolution'];
  var index_data = index['index'];
  var date;
  for (var i = 0; i < index['end_ts'].length; i++){
      date = new Date(index["end_ts"][i] * 1000).format("yyyy年MM月dd日 hh:mm:ss");
      index_time.push(date);
  }
  curr = data;
  draw_index(); 
}

function draw_index(){
      $("#index").height(600);
      $('#index').empty();
      $('#textarea').empty();
      $('#textarea').append('<textarea cols = 50 rows = 2>当前舆情指数:30.2%，属于:中等偏下。</textarea>');
      
        var value = curr["last_index"].toFixed(3)*100;
        var index_data = [{value: value, name: '舆情指数'}];

    var option = {
        tooltip: {
            formatter: "{a} <br/>{b} : {c}%"
        },
        title : {
            text: '',
            x: 'center'
        },
        toolbox: {
            show : true,
            x:"left",
            feature : {
                dataView : {show: true, readOnly: false},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        series : [
            {
                name:'舆情指数',
                type:'gauge',
                center : ['50%', '39%'],    // 默认全局居中
                radius : ['50%','74%'],
                startAngle: 140,
                endAngle : -140,
                min: 0,                     // 最小值
                max: 100,                   // 最大值
                precision: 3,               // 小数精度，默认为0，无小数点
                splitNumber: 10,             // 分割段数，默认为5
                axisLine: {            // 坐标轴线
                    show: true,        // 默认显示，属性show控制显示与否
                    lineStyle: {       // 属性lineStyle控制线条样式
                        color: [[0.2, 'lightgreen'],[0.4, 'orange'],[0.8, 'skyblue'],[1, '#ff4500']], //划分区域，对不同的指标可以修改预警的数值范围
                        width: 40
                    }
                },
                axisTick: {            // 坐标轴小标记
                    show: true,        // 属性show控制显示与否，默认不显示
                    splitNumber: 5,    // 每份split细分多少段
                    length :5,         // 属性length控制线长
                    lineStyle: {       // 属性lineStyle控制线条样式
                        color: '#eee',
                        width: 1,
                        type: 'solid'
                    }
                },
                axisLabel: {           // 坐标轴文本标签，详见axis.axisLabel
                    show: true,
                    formatter: function(v){
                        switch (v+''){
                            case '10': return '弱';
                            case '30': return '低';
                            case '60': return '中';
                            case '90': return '高';
                            default: return '';
                        }
                    },
                    textStyle: {       // 其余属性默认使用全局文本样式，详见TEXTSTYLE
                        color: '#320',
                        fontSize : 10
                    }
                },
                splitLine: {           // 分隔线
                    show: true,        // 默认显示，属性show控制显示与否
                    length :10,         // 属性length控制线长
                    lineStyle: {       // 属性lineStyle（详见lineStyle）控制线条样式
                        color: '#eee',
                        width: 2,
                        type: 'solid'
                    }
                },
                pointer : {
                    length : '80%',
                    width : 8,
                    color : 'auto'
                },
                title : {
                    show : true,
                    offsetCenter: ['-80%', -5],       // x, y，单位px
                    textStyle: {       // 其余属性默认使用全局文本样式，详见TEXTSTYLE
                        color: '#333',
                        fontSize : 15,
                        fontWeight: 'bolder'
                    }
                },
                detail : {
                    show : true,
                    backgroundColor: 'rgba(0,0,0,0)',
                    borderWidth: 0,
                    borderColor: '#ccc',
                    width: 100,
                    height: 40,
                    offsetCenter: ['-80%', -2],       // x, y，单位px
                    formatter:'{value}%',
                    textStyle: {       // 其余属性默认使用全局文本样式，详见TEXTSTYLE
                        color: 'red',
                        fontSize : 15,
                        fontWeight: 'bolder'
                    }
                },
                data:index_data
            },
 
        ]
    };
    var myChart = echarts.init(document.getElementById('index'));
    myChart.setOption(option);
}

function json_data(){
    $("#index").height(800);
    $('#index').empty();
     $('#textarea').empty();
    var curr_data = curr['now_system'];
    var json_data = {};
    var f_involved = {};
    var f_sensitivity = {};
    var f_sentiment = {};
    var f_transmission = {};
    
    var class_sensitivity = {};
    var coverage = {};
    var duration = {};
    var media_involved ={};
    var person_involved = {};
    var quickness = {};
    var sentiment_angry = {};
    var sentiment_sad = {};
    var word_sensitivity = {};

    json_data["name"] = "舆情指数[ " + curr_data['index'][0] +"/"+curr_data['index'][1].toFixed(2).toString()+" ]" ;
    f_transmission["name"] ='传播强度指数['+ curr_data['f_transmission'][0] +"/"+curr_data['f_transmission'][1].toFixed(2).toString()+" ]" ;
    f_sentiment["name"] = '负面情绪指数['+ curr_data['f_sentiment'][0] +"/"+curr_data['f_sentiment'][1].toFixed(2).toString()+" ]" ;
    f_involved["name"] = "主体敏感指数["+ curr_data['f_invovled'][0] +"/"+curr_data['f_invovled'][1].toFixed(2).toString()+" ]" ;
    f_sensitivity["name"] = '事件敏感指数['+ curr_data['f_sensitivity'][0] +"/"+curr_data['f_sensitivity'][1].toFixed(2).toString()+" ]" ;

    class_sensitivity['name'] = '类型敏感度['+ curr_data['class_sensitivity'][0] +"/"+curr_data['class_sensitivity'][1].toFixed(2).toString()+" ]" ;
    coverage['name'] = "传播覆盖度["+ curr_data['coverage'][0].toFixed(2).toString() +"/"+curr_data['coverage'][1].toFixed(2).toString()+" ]" ;
    duration["name"] = '传播持续度['+ curr_data['duration'][0].toFixed(2).toString() +"/"+curr_data['duration'][1].toFixed(2).toString()+" ]";
    media_involved["name"] = '总要媒体参与度['+ curr_data['media_involved'][0] +"/"+curr_data['media_involved'][1].toFixed(2).toString()+" ]";
    person_involved["name"] = '敏感人物参与度['+ curr_data['person_involved'][0] +"/"+curr_data['person_involved'][1].toFixed(2).toString()+" ]";
    quickness["name"] = '传播爆发度['+ curr_data['quickness'][0].toFixed(2).toString() +"/"+curr_data['quickness'][1].toFixed(2).toString()+" ]";
    sentiment_angry["name"] = '愤怒情绪度['+ curr_data['sentiment_angry'][0] +"/"+curr_data['sentiment_angry'][1].toFixed(2).toString()+" ]";
    sentiment_sad["name"] = '悲伤情绪度['+ curr_data['sentiment_sad'][0] +"/"+curr_data['sentiment_sad'][1].toFixed(2).toString()+" ]";
    word_sensitivity["name"] = '内容敏感度['+ curr_data['word_sensitivity'][0] +"/"+curr_data['word_sensitivity'][1].toFixed(2).toString()+" ]";

    class_sensitivity['size'] = 0.3;
    duration['size'] = 0.3;
    media_involved['size'] = 0.3;
    person_involved['size'] = 0.3;
    quickness['size'] = 0.3;
    sentiment_angry['size'] = 0.3;
    sentiment_sad['size'] = 0.3;
    coverage['size'] = 0.3;
    word_sensitivity['size'] = 0.3;

    f_transmission["children"] = [coverage,duration,quickness];
    f_sentiment["children"] = [sentiment_angry,sentiment_sad];
    f_involved["children"] = [class_sensitivity,word_sensitivity];
    f_sensitivity["children"] = [person_involved,media_involved];
    json_data["children"] = [f_involved,f_sentiment,f_transmission,f_sensitivity];
    console.log(json_data);
    


    var tree = d3.layout.tree()
        .size([h, w]);

    var diagonal = d3.svg.diagonal()
        .projection(function(d) { return [d.y, d.x]; });

    var vis = d3.select("#index").append("svg:svg")
        .attr("width", w + m[1] + m[3])
        .attr("height", h + m[0] + m[2])
      .append("svg:g")
        .attr("transform", "translate(" + m[3] + "," + m[0] + ")");

     
      root = json_data;
      root.x0 = h / 2;
      root.y0 = 0;

      function toggleAll(d) {
        if (d.children) {
          d.children.forEach(toggleAll);
          console.log(d.children);
          toggle(d);
        }
      }
      update(root,tree,vis,diagonal,root);
}



var m = [20, 120, 20, 120],
w = 1000 - m[1] - m[3],
h = 800 - m[0] - m[2],
i = 0,
root;
function update(source,tree,vis,diagonal,root) {
  var duration = d3.event && d3.event.altKey ? 5000 : 500;

  // Compute the new tree layout.
  var nodes = tree.nodes(root).reverse();

  // Normalize for fixed-depth.
  nodes.forEach(function(d) { d.y = d.depth * 180; });

  // Update the nodes…
  var node = vis.selectAll("g.node")
      .data(nodes, function(d) { return d.id || (d.id = ++i); });

  // Enter any new nodes at the parent's previous position.
  var nodeEnter = node.enter().append("svg:g")
      .attr("class", "node")
      .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
      .on("click", function(d) { toggle(d); update(d); });

  nodeEnter.append("svg:circle")
      .attr("r", 10)    
      .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

  nodeEnter.append("svg:text")
      .attr("x", function(d) { return d.children || d._children ? -10 : 10; })
      .attr("dy", ".35em")
      .attr("text-anchor", function(d) { return d.children || d._children ? "end" : "start"; })
      .text(function(d) { return d.name; })
      .style("fill-opacity", 1e-6);
  

  // Transition nodes to their new position.
  var nodeUpdate = node.transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });

  nodeUpdate.select("circle")
      .attr("r", 4.5)
      .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

  nodeUpdate.select("text")
      .style("fill-opacity", 1);

  // Transition exiting nodes to the parent's new position.
  var nodeExit = node.exit().transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
      .remove();

  nodeExit.select("circle")
      .attr("r", 1e-6);

  nodeExit.select("text")
      .style("fill-opacity", 1e-6);

  // Update the links…
  var link = vis.selectAll("path.link")
      .append("line")
      .data(tree.links(nodes), function(d) { return d.target.id; });
      // .style("stroke-width",1);
      

  // Enter any new links at the parent's previous position.
  link.enter().insert("svg:path", "g")
      .attr("class", "link")
      .attr("d", function(d) {
        var o = {x: source.x0, y: source.y0};
        return diagonal({source: o, target: o});
      })
    .transition()
      .duration(duration)
      .attr("d", diagonal);

  // Transition links to their new position.
  link.transition()
      .duration(duration)
      .attr("d", diagonal);

  // Transition exiting nodes to the parent's new position.
  link.exit().transition()
      .duration(duration)
      .attr("d", function(d) {
        var o = {x: source.x, y: source.y};
        return diagonal({source: o, target: o});
      })
      .remove();

  // Stash the old positions for transition.
  nodes.forEach(function(d) {
    d.x0 = d.x;
    d.y0 = d.y;
  });
}

// Toggle children.
function toggle(d) {
  if (d.children) {
    d._children = d.children;
    d.children = null;
  } else {
    d.children = d._children;
    d._children = null;
  }

  if(d.name = "sensitivity"){
       draw_sensitivity();
  }
//可以用来做任何的点击事件
}

function draw_line(){
  $("#index").height(450);
  $('#index').empty();
  $('#textarea').empty();
     var quota = curr['f_quota_evolution']; 
     console.log(quota);
    $('#index').highcharts({
        title: {
            text: '',
            x: -20 //center
        },
        chart: { 
          defaultSeriesType: 'spline', //图表类型line(折线图), 放 
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
        plotOptions: {
         spline: {
              lineWidth: 2,
              marker: {
                  enabled: false
              },
           }
          },
        xAxis: {
            categories: index_time
        },
        yAxis: {
            title: {
                text: ''
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
            name: '舆情指数',
            data: curr["index_evolution"]["index"]
        },
        {
            name: '事件敏感指数',
            data: quota["f_sensitivity"] 
        }, {
            name: '负面情绪指数',
            data: quota['f_sentiment'] 
        }, {
            name: '传播强度指数',
            data: quota['f_transmission'] 
        }, {
            name: '主体敏感指数',
            data: quota["f_involved"]
        }],
      })
}
