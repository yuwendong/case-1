 var topic = QUERY; 
 var attention_value = [];
 var quickness_value = [];
 var attention_all = 0;
 var quickness_all = 0;
 var attention_value;
 var quickness_value; 
 var attention;
 var quickness;
 var quota = {};
 var attention_index = []
 var sensitivity;
 var sensitivity_value = [];
 var sensitivity_all = 0;
 var sensitivity_average = 0;
 var attention_average = 0;
 var quickness_average = 0;
$(document).ready(function(){
    getindex_data();
    draw_index();
    draw_quickness();
    draw_attention();

 })
 function getindex_data(){
        $.ajax({
        url:"/quota_system/topic/?topic="+topic,
        dataType: "json",
        type: "GET",
        async:false,  //最好用回调函数
        success :function(data){
            quota = data;
            
            console.log(data);          
        }       
    });

    attention = quota['attention'];
    quickness = quota['quickness'];
    sensitivity = quota['sensitivity'];
    //  sensitivity = quota['sensitivity'];
    for (var key in attention){
        attention_value.push(attention[key]);
        // console.log(key);
        var key_index = '';
        if (key == 'folk'){
             key_index = '民众';
        }
        console.log(key_index);
        if (key == 'opinion_leader'){
           key_index = '名人';
        }
        if (key == 'media'){
          key_index = '媒体';
        }
        if (key == 'other'){
          key_index = '其他';
        }
        if (key == 'oversea'){
          key_index = '海外';
        }
        attention_index.push(key_index);
    }
    // console.log(attention_index);
    // console.log(attention_value);


    for (var i=0 ;i<attention_value.length;i++){
         // console.log(attention_value[0]);
        attention_all += attention_value[i];
    }
            attention_average = attention_all/5;


    for (var key in quickness){
        quickness_value.push(quickness[key]);
    }
    console.log(quickness);
    for (var i=0 ;i<quickness_value.length;i++){
        quickness_all += quickness_value[i];
    }

            quickness_average = quickness_all/5;

        for (var key in sensitivity){
             console.log(sensitivity[key]);
        sensitivity_value.push(sensitivity[key]);
    }

    for (var i=0 ;i<sensitivity_value.length;i++){
         console.log(attention_value[0]);
        sensitivity_all += sensitivity_value[i];
    }
        sensitivity_average = sensitivity_all/3;
        json_data(quota); 
 }

function json_data(data){
    var json_data = {};
    var content_data = {};
    var process_data = {};
    var sensitivity_data = {};
    var attention_data = {};
    var quickness_data = {};
    var importance_data = {};
    var sentiment_data = {};
    var media_importance_data ={};
    var duration_data = {};
    var area = {};
    var root = "舆情总度";
    var duration = data["duration"];
    var media_importance = data["media_importance"];
    var attention_folk = data["attention"]["folk"];
    var attention_media = data["attention"]["media"];
    var attention_opinion_leader = data["attention"]["opinion_leader"];
    var attention_other = data["attention"]["other"];
    var attention_oversea = data["attention"]["oversea"];
    var quickness_folk = data["attention"]["folk"];
    var quickness_media = data["attention"]["media"];
    var quickness_opinion_leader = data["attention"]["opinion_leader"];
    var quickness_other = data["attention"]["other"];
    var quickness_oversea = data["attention"]["oversea"];
    var sensitivity_1 = data["sensitivity"]["1"];
    var sensitivity_2 = data["sensitivity"]["2"];
    var sensitivity_3 = data["sensitivity"]["3"];
    var area_data= data["geo_penetration"];
    var score = data["importance"]["score"];
    var weight = data["importance"]["weight"];
    var negative = data['sentiment']['negative'];
    var positive = data["sentiment"]['positive'];
    
    var attention_weight = data['quota_weight']['attention'];
    var duration_weight = data['quota_weight']['duration'];
    var geo_penteration_weight = data['quota_weight']['geo_penetration'];
    var media_importance_weight = data['quota_weight']['media_importance'];
    var sensitivity_weight = data['quota_weight']['sensitivity'];
    var sentiment_weight = data['quota_weight']['sentiment'];
    var human_mmedia ={};

    human_mmedia["name"] = "人物重要度"
    json_data["name"] = root ;
    content_data["name"] = "内容重要度"+'['+0.5.toExponential(2).toString()+"/"+0.5.toExponential(2).toString()+']';
    process_data["name"] = "传播重要度"+'['+0.5.toExponential(2).toString()+"/"+0.5.toExponential(2).toString()+']';;
    sensitivity_data["name"] = "敏感度: "+'['+sensitivity_average.toExponential(2).toString()+"/"+sensitivity_weight.toExponential(2).toString()+"]";
    attention_data["name"] = "关注度: "+'['+attention_average.toExponential(2).toString()+"/"+attention_weight.toExponential(2).toString()+"]";
    quickness_data["name"] = "爆发度: "+'['+quickness_average.toExponential(2).toString()+"/ 0.0e+0"+"]";
    sentiment_data["name"] = "情绪度："+"[0.50e-1/0.00e+0]";          
    importance_data["name"] = "专家重视度"+"[0.0e+0/0.0e+0]";
    media_importance_data["name"] = "重要媒体参与度: "+'['+data["media_importance"].toExponential(2).toString()+"/"+media_importance_weight.toExponential(2).toString()+"]";
    duration_data["name"] = "持续度: "+'['+ data["duration"].toExponential(2).toString()+"/"+duration_weight.toExponential(2).toString()+"]";
    area["name"] = "地域渗透度"+'['+area_data.toExponential(2).toString() +"/"+geo_penteration_weight.toExponential(2).toString()+"]";

    human_mmedia['children'] = [{"name":"重要媒体参与度"+'['+data["media_importance"].toExponential(2)+'/'+media_importance_weight.toExponential(2).toString()+']', "size":data["media_importance"]},{"name":"敏感人物参与度"+'['+data["media_importance"].toExponential(2).toString()+'/'+media_importance_weight.toExponential(2).toString()+']' ,"size":data["media_importance"]}]
    area["size"] = area_data;
    quickness_data["size"] =0.8 //[{"name":"民众"+quickness_folk.toExponential(2), "size":quickness_folk},{"name":"媒体"+quickness_media.toExponential(1), "size":quickness_media},{"name":"名人"+quickness_opinion_leader.toExponential(1), "size":quickness_opinion_leader},{"name":"海外"+quickness_oversea.toExponential(1), "size":quickness_oversea},{"name":"其他"+quickness_other.toExponential(1), "size":quickness_other}];
    attention_data["size"] =0.4 //[{"name":"民众"+attention_folk.toExponential(2), "size":attention_folk},{"name":"媒体"+attention_media.toExponential(1), "size":attention_media},{"name":"名人"+attention_opinion_leader.toExponential(1), "size":attention_opinion_leader},{"name":"海外"+attention_oversea.toExponential(1), "size":attention_oversea},{"name":"其他"+attention_other.toExponential(1), "size":attention_other}];
    sensitivity_data["children"] = [{"name":"类型敏感度" +'['+sensitivity_1.toExponential(2).toString()+'/'+sensitivity_1.toExponential(2).toString()+']',"size":sensitivity_1},{"name":"词汇敏感度"+'['+sensitivity_2.toExponential(2).toString()+'/'+sensitivity_2.toExponential(2).toString()+']' ,"size":sensitivity_2},{"name":"地域敏感度"+'['+sensitivity_3.toExponential(2).toString()+'/'+sensitivity_3.toExponential(2).toString()+']' ,"size":sensitivity_3}];
    sentiment_data["children"] = [{"name": "消极情绪度: "+'['+data['sentiment']['negative'].toExponential(2)+'/'+0.5.toExponential(2).toString()+']',"size":negative},{"name": "积极情绪度: "+'['+data['sentiment']['positive'].toExponential(2)+'/'+0.5.toExponential(2).toString()+']',"size":positive}];
    //importance_data["children"] = [{"name":"值" ,"size":score},{"name":"权重" ,"size":weight}];
    importance_data["size"] = '0';
    media_importance_data["size"] = media_importance;
    duration_data["size"] = data["duration"];
    content_data["children"] = [sensitivity_data, sentiment_data];
    process_data["children"] = [duration_data, quickness_data,attention_data,area, human_mmedia];
    json_data["children"] = [importance_data, content_data, process_data];
    drawtree(json_data);
}
var m = [20, 120, 20, 120],
    w = 1000 - m[1] - m[3],
    h = 800 - m[0] - m[2],
    i = 0,
    root;

var tree = d3.layout.tree()
    .size([h, w]);

var diagonal = d3.svg.diagonal()
    .projection(function(d) { return [d.y, d.x]; });

var vis = d3.select("#body").append("svg:svg")
    .attr("width", w + m[1] + m[3])
    .attr("height", h + m[0] + m[2])
  .append("svg:g")
    .attr("transform", "translate(" + m[3] + "," + m[0] + ")");

 function drawtree(json) {
  root = json;
  root.x0 = h / 2;
  root.y0 = 0;

  function toggleAll(d) {
    if (d.children) {
      d.children.forEach(toggleAll);
      console.log(d.children);
      toggle(d);
    }
  }


  // Initialize the display to show a few nodes.
  //root.children.forEach(toggleAll);
  // toggle(root.children[1]);
  // toggle(root.children[1].children[2]);
  // toggle(root.children[9]);
  // toggle(root.children[9].children[0]);

  update(root);
}

function update(source) {
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
      .attr("r", 1e-6)
      .attr("data-toggle", function(d) {if(d.name =="敏感度: "+sensitivity_average.toExponential(3).toString() ||  "爆发度: "+quickness_average.toExponential(3).toString() || "关注度: "+attention_average.toExponential(3).toString() ) return "modal" ; })
      .attr("data-target", function(d) {if(d.name =="敏感度: "+sensitivity_average.toExponential(3).toString()) return "#sensitivity_1" ; else if (d.name =="爆发度: "+quickness_average.toExponential(3).toString()) return "#quickness_1";else if (d.name == "关注度: "+attention_average.toExponential(3).toString()) return "#attention_1";})
      // .attr("data-toggle", function(d) {if(d.name =="quickness") return "modal" ; })
      // .attr("data-target", function(d) {if(d.name =="quickness") return "#quickness_1" ; })
      // .attr("data-toggle", function(d) {if(d.name =="attention") return "modal" ; })
      // .attr("data-target", function(d) {if(d.name =="attention") return "#attention_1" ; })      
      .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

  nodeEnter.append("svg:text")
      .attr("x", function(d) { return d.children || d._children ? -10 : 10; })
      .attr("dy", ".35em")
      .attr("id",function(d){if(d.name =="舆情总度") return "total"})
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
      .data(tree.links(nodes), function(d) { return d.target.id; });

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

  // if(d.name = "sensitivity"){
  //      draw_sensitivity();
  // }
//可以用来做任何的点击事件
}
// function draw_sensitivity(){
//     console.log("abc");
//     draw_index();
// }

function draw_index(){
        console.log("index");
        var labelTop = {
        normal : {
            label : {
                show : true,
                position : 'center',
                textStyle: {
                    baseline : 'bottom'
                }
            },
            labelLine : {
                show : false
            }
        }
    };
    var labelBottom = {
        normal : {
            color: '#ccc',
            label : {
                show : true,
                position : 'center',
                formatter : function (a,b,c){return 100 - c + '%'},
                textStyle: {
                    baseline : 'top'
                }
            },
            labelLine : {
                show : false
            }
        },
        emphasis: {
            color: 'rgba(0,0,0,0)'
        }
    };
    var radius = [55, 70];
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
                name:'类型敏感度',
                type:'gauge',
                center : ['20%', '30%'],    // 默认全局居中
                radius : radius,
                startAngle: 140,
                endAngle : -140,
                min: 0,                     // 最小值
                max: 100,                   // 最大值
                precision: 0,               // 小数精度，默认为0，无小数点
                splitNumber: 10,             // 分割段数，默认为5
                axisLine: {            // 坐标轴线
                    show: true,        // 默认显示，属性show控制显示与否
                    lineStyle: {       // 属性lineStyle控制线条样式
                        color: [[0.2, 'lightgreen'],[0.4, 'orange'],[0.8, 'skyblue'],[1, '#ff4500']], //划分区域，对不同的指标可以修改预警的数值范围
                        width: 15
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
                data:[{value: 0, name: '类型敏感度'}]
            },
            {
                name:'地域敏感度',
                type:'gauge',
                center : ['50%', '30%'],    // 默认全局居中
                radius : radius,
                startAngle: 140,
                endAngle : -140,
                min: 0,                     // 最小值
                max: 100,                   // 最大值
                precision: 0,               // 小数精度，默认为0，无小数点
                splitNumber: 10,             // 分割段数，默认为5
                axisLine: {            // 坐标轴线
                    show: true,        // 默认显示，属性show控制显示与否
                    lineStyle: {       // 属性lineStyle控制线条样式
                        color: [[0.2, 'lightgreen'],[0.4, 'orange'],[0.8, 'skyblue'],[1, '#ff4500']], //划分区域，对不同的指标可以修改预警的数值范围
                        width: 15
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
                data:[{value: 0, name: '地域敏感度'}]
            },
            {
                name:'词汇敏感度',
                type:'gauge',
                center : ['80%', '30%'],    // 默认全局居中
                radius : radius,
                startAngle: 140,
                endAngle : -140,
                min: 0,                     // 最小值
                max: 100,                   // 最大值
                precision: 0,               // 小数精度，默认为0，无小数点
                splitNumber: 10,             // 分割段数，默认为5
                axisLine: {            // 坐标轴线
                    show: true,        // 默认显示，属性show控制显示与否
                    lineStyle: {       // 属性lineStyle控制线条样式
                        color: [[0.2, 'lightgreen'],[0.4, 'orange'],[0.8, 'skyblue'],[1, '#ff4500']], //划分区域，对不同的指标可以修改预警的数值范围
                        width: 15
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
                data:[{value: 0, name: '词汇敏感度'}]
            },
 
        ]
    };
    var myChart = echarts.init(document.getElementById('sensivity'));
    myChart.setOption(option);
}

function draw_quickness(){
 var option = {
    title : {
        text: '',
    },
    tooltip : {
        trigger: 'axis'
    },
    legend: {
        data:['关注度', '爆发度']
    },
    toolbox: {
         x:"left",
        show : true,
        feature : {
            dataView : {show: true, readOnly: false},
            magicType: {show: true, type: ['line', 'bar']},
            saveAsImage : {show: true}
        }
    },
    calculable : true,
    xAxis : [
        {   splitNumber: 1,
            type : 'value',
            boundaryGap : [0, 0.01]
        }
    ],
    yAxis : [
        {
            type : 'category',
            data : attention_index
        }
    ],
    series : [
        {
            name:'关注度',
            type:'bar',
            data:attention_value
        },
        {
            name:'爆发度',
            type:'bar',
            data:quickness_value
        }
    ]
};
    var myChart = echarts.init(document.getElementById('quickness'));
    myChart.setOption(option);                
}

function draw_attention(){
var option = {
    title : {
        text: '',
    },
    tooltip : {
        trigger: 'axis'
    },
    legend: {
        data:['关注度', '爆发度']
    },
    toolbox: {
        x:"left",
        show : true,
        feature : {
            dataView : {show: true, readOnly: false},
            magicType: {show: true, type: ['line', 'bar']},
            saveAsImage : {show: true}
        }
    },
    calculable : true,
    xAxis : [
        {   splitNumber: 1,
            type : 'value',
            boundaryGap : [0, 0.01]
        }
    ],
    yAxis : [
        {
            type : 'category',
            data : attention_index
        }
    ],
    series : [
        {
            name:'关注度',
            type:'bar',
            data:attention_value
        },
        {
            name:'爆发度',
            type:'bar',
            data:quickness_value
        }
    ]
};
                    
    var myChart = echarts.init(document.getElementById('attention'));
    myChart.setOption(option);                
}





