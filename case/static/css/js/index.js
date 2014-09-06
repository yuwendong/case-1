 var topic = "中国";
 var quota = {}; 
 var attention_value = [];
 var quickness_value = [];
 var attention;
 var quickness; 
$(document).ready(function(){
    drawpicture_bar();
    draw_index();
    getindex_data();

 })
 function getindex_data(){
var  name = ['duration','geo_penetration','media_importance','attention','quickness','sensitivity'];
     for ( var key in name){
        $.ajax({
        url:"/quota_system/topic/?topic="+topic+ '&quota=' + name[key],
        dataType: "json",
        type: "GET",
        success :function(data){
            quota[name[key]] = data;  
        }       
    });
    }
     console.log(quota['duration']);
    //  attention = quota['attention'];
    //  quickness = quota['quickness'];
    //  sensitivity = quota['sensitivity'];
    //  for (var i = 0 ;i< attention.length; i++){
    //       attention_all += attention_all[i]; 
    //     attention_value.push = attention[i]
    //  }
    //   attention_average = attention_all/5;
    // for (var i = 0 ;i< quickness.length; i++){
    //     quickness_all += quickness[i]; 
    //     quickness_value.push = quickness[i]
    //  }
    //   quickness_average = quickness_all/5;
    // for (var i = 0 ;i< sensitivity.length; i++){
    //     sensitivity_all += sensitivity[i]; 
    //     sensitivity_value.push = sensitivity[i]
    //  }
    //   sensitivity_average = sensitivity_all/3;

 
var html ='';
  html += "<tr>"
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">重要媒体参与度<span class=\"tsp\">   : </span>" +quota['media_importance'] +"</div><div class=\"lrRr\"></div></div></th>";
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">持续度<span class=\"tsp\">   : </span>" + quota['duration'] +"</div><div class=\"lrRr\"></div></div></th></tr>";
  html += "<tr>"
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">地域渗透度<span class=\"tsp\">   : </span>" + quota['geo_penetration'] +"</div><div class=\"lrRr\"></div></div></th></tr>";

  html += "<tr>"
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">关注度<span class=\"tsp\">   : </span>" +'0.12131' +"</div><div class=\"lrRr\"></div></div></th>";
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">爆发度<span class=\"tsp\">   : </span>" +'0.32632' +"</div><div class=\"lrRr\"></div></div></th></tr>";
  $("#mstable").append(html);
  var html1 ='';
  html1 += "<tr>"
  html1 += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">情绪度<span class=\"tsp\">   : </span>" +'0.323728' +"</div><div class=\"lrRr\"></div></div></th></tr>";
  html1 += "<tr>"
  html1 += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">敏感度<span class=\"tsp\">   : </span>" +'0.323728' +"</div><div class=\"lrRr\"></div></div></th></tr>";
  $("#mstable1").append(html1);

 }

// function show_text(){ 
//     $("#text_graph").show(); 
// }

 function drawpicture_bar(){
 option = {
    title : {

        text: ''
    },
    tooltip : {
        trigger: 'axis'
    },
    legend: {
        data:['关注度','爆发度']
    },
    toolbox: {
        show : true,
        feature : {
            mark : {show: true},
            dataView : {show: true, readOnly: false},
            magicType : {show: true, type: ['line', 'bar']},
            restore : {show: true},
            saveAsImage : {show: true}
        }
    },
    calculable : true,
    xAxis : [
        {
            type : 'category',
            data : ['民众','媒体','名人','海外','其他']
        }
    ],
    yAxis : [
        {
            type : 'value'
        }
    ],
    series : [
        {
            name:'关注度',
            type:'bar',
            data:[2.0, 4.9, 7.0, 23.2, 25.6]
        },
        {
            name:'爆发度',
            type:'bar',
            data:[2.6, 5.9, 9.0, 26.4, 28.7]
        }
    ]
};
    var myChart = echarts.init(document.getElementById('main'));
    myChart.setOption(option);
}


function draw_index(){
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
            x: 'center',
        textStyle:{
        fontSize: 14,
        }
        },
        toolbox: {
            show : true,
            feature : {
                dataView : {show: true, readOnly: false},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        series : [
            {
                name:'类型',
                type:'gauge',
                center : ['30%', '25%'],    // 默认全局居中
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
                data:[{value: 10, name: '类型'}]
            },
            {
                name:'词汇',
                type:'gauge',
                center : ['55%', '25%'],    // 默认全局居中
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
                    length : '90%',
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
                data:[{value: 50, name: '词汇'}]
            },
            {
                name:'地域',
                type:'gauge',
                center : ['80%', '25%'],    // 默认全局居中
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
                data:[{value: 20, name: '地域'}]
            }
        ]
    };
    var myChart = echarts.init(document.getElementById('index'));
    myChart.setOption(option);
}