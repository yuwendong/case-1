var topic = QUERY;
if(topic == '中国'){
  var start_ts = 1377964800 + 900;
}
else{
  var start_ts = START_TS;
}
var end_ts = END_TS;
var network_type2 = 2;//源头转发网络是1，直接上级转发网络是2
var previous_data = null;
var current_data = null;
var networkShowed = 0;
var networkUpdated2 = 0;
var animation = 0;
var sigInst = null;
var animation_timer = null;
var quota={};
var networkdata ;
var rankdata;
var node;
var y_data;

function get_network_infor2(){
var  name = ['number_edges', 'number_nodes','ave_degree'];
  for ( var key in name){
    $.ajax({
        url: "/identify/quota/?topic="+ topic +'&start_ts=' + start_ts +'&end_ts=' + end_ts +'&quota=' + name[key] + '&network_type=' + network_type2,
        dataType : "json",
        type : 'GET',
        async: false,
        success: function(data){
            quota[name[key]] = data;
        }

    }) ; 
  }
  $("#mstable2").empty();
  var html ='';
  html += "<tr>"
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">总节点数<span class=\"tsp\">   : </span>" +quota['number_nodes'] +"</div><div class=\"lrRr\"></div></div></th>";
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">总边数<span class=\"tsp\">   : </span>" +quota['number_edges'] +"</div><div class=\"lrRr\"></div></div></th>";
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">平均节点度<span class=\"tsp\">   : </span>" +quota['ave_degree'] +"</div><div class=\"lrRr\"></div></div></th></tr>";
  $("#mstable2").append(html);
}

function get_network_infor3(){
var  name = ['number_edges', 'number_nodes','ave_degree_centrality', 'ave_betweenness_centrality',
 'ave_closeness_centrality','number_strongly_connected_components',
 'average_shortest_path_length','ave_eccentricity','power_law_distribution','ave_degree',
 'diameter','power_law_distribution','number_weakly_connected_components',
 'degree_assortativity_coefficient','average_clustering'];
  for ( var key in name){
    $.ajax({
        url: "/identify/quota/?topic="+ topic +'&start_ts=' + start_ts +'&end_ts=' + end_ts +'&quota=' + name[key] + '&network_type=' + network_type2,
        dataType : "json",
        type : 'GET',
        async: false,
        success: function(data){
            quota[name[key]] = data;
        }

    }) ; 
  }
  $("#mstable3").empty();
  var html ='';
  html += "<tr>"
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">幂律分布系数<i id=\"power_law_distribution_tooltip\" class=\"glyphicon glyphicon-question-sign\" style=\"color:#2894FF\"data-toggle=\"tooltip\" data-placement=\"right\" title=\"度分布进行幂律分布拟合得到的系数\"></i>&nbsp;&nbsp;<span class=\"tsp\">   : </span>" +quota['power_law_distribution'].toExponential(2) +"</div><div class=\"lrRr\"></div></div></th>";
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">平均度中心性<i id=\"trend_tooltip\" class=\"glyphicon glyphicon-question-sign\" style=\"color:#2894FF\"data-toggle=\"tooltip\" data-placement=\"right\" title=\"单点度中心性即节点的所有连接数除以可能的最大连接数\"></i>&nbsp;&nbsp;<span class=\"tsp\">   : </span>" +quota['ave_degree_centrality'].toExponential(2) +"</div><div class=\"lrRr\"></div></div></th>";
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">平均介数中心性<i id=\"trend_tooltip\" class=\"glyphicon glyphicon-question-sign\" style=\"color:#2894FF\"data-toggle=\"tooltip\" data-placement=\"right\" title=\"单点介数中心性即所有的节点对之间通过该节点的最短路径条数\"></i>&nbsp;&nbsp;<span class=\"tsp\">   : </span>" +quota['ave_betweenness_centrality'].toExponential(2) +"</div><div class=\"lrRr\"></div></div></th></tr>";
  html += "<tr>"
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">平均紧密中心性<i id=\"trend_tooltip\" class=\"glyphicon glyphicon-question-sign\" style=\"color:#2894FF\"data-toggle=\"tooltip\" data-placement=\"right\" title=\"单点紧密中心性即节点到达它可达节点的平均距离\"></i>&nbsp;&nbsp;<span class=\"tsp\">   : </span>" +quota['ave_closeness_centrality'].toExponential(2) +"</div><div class=\"lrRr\"></div></div></th>";
  //html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">平均特征向量中心性<i id=\"trend_tooltip\" class=\"glyphicon glyphicon-question-sign\" style=\"color:#2894FF\"data-toggle=\"tooltip\" data-placement=\"right\" title=\"基于“高指数节点的连接对一个节点的贡献度比低指数节点的贡献度高”这一原则，每个节点都有一个相对指数值\"></i>&nbsp;&nbsp;<span class=\"tsp\">   : </span>" +quota['eigenvector_centrality'].toExponential(2) +"</div><div class=\"lrRr\"></div></div></th>";
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">同配性系数<i id=\"trend_tooltip\" class=\"glyphicon glyphicon-question-sign\" style=\"color:#2894FF\"data-toggle=\"tooltip\" data-placement=\"right\" title=\"如果总体上度大的节点倾向于连接度大的节点，那么网络同配。同配性系数用作考察度值相近的节点是否倾向于互相连接\"></i>&nbsp;&nbsp;<span class=\"tsp\">   : </span>"+quota['degree_assortativity_coefficient'].toExponential(2)+"</div><div class=\"lrRr\"></div></div></th>";
  //html += "<tr>"
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">平均聚类系数<i id=\"trend_tooltip\" class=\"glyphicon glyphicon-question-sign\" style=\"color:#2894FF\"data-toggle=\"tooltip\" data-placement=\"right\" title=\"单点聚类系数即某节点的邻居节点间实际存在的边数与总的可能存在的边数之比\"></i>&nbsp;&nbsp;<span class=\"tsp\">   : </span>"+quota['average_clustering'].toExponential(2)+"</div><div class=\"lrRr\"></div></div></th></tr>";
  html += "<tr>"
  html +="<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">平均最短路径长度<i id=\"trend_tooltip\" class=\"glyphicon glyphicon-question-sign\" style=\"color:#2894FF\"data-toggle=\"tooltip\" data-placement=\"right\" title=\"网络中任意两节点间最短路径长度的均值\"></i>&nbsp;&nbsp;<span class=\"tsp\">   : </span>"+quota['average_shortest_path_length'].toExponential(2)+"</div><div class=\"lrRr\"></div></div></th>";
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">直径<i id=\"trend_tooltip\" class=\"glyphicon glyphicon-question-sign\" style=\"color:#2894FF\"data-toggle=\"tooltip\" data-placement=\"right\" title=\"网络中任意两个节点之间距离的最大值为网络直径\"></i>&nbsp;&nbsp;<span class=\"tsp\">   : </span>" +quota['diameter'] +"</div><div class=\"lrRr\"></div></div></th>";
  //html += "<tr>"
  html +="<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">平均离心率<i id=\"trend_tooltip\" class=\"glyphicon glyphicon-question-sign\" style=\"color:#2894FF\"data-toggle=\"tooltip\" data-placement=\"right\" title=\"单点偏心率计算了单点偏离中心的程度\"></i>&nbsp;&nbsp;<span class=\"tsp\">   : </span>"+quota['ave_eccentricity'].toExponential(2)+"</div><div class=\"lrRr\"></div></div></th></tr>";
  $("#mstable3").append(html);
}
 
 // function bindmore_infor(html){
 // 	var target = document.getElementById('trendProfile2');
 // 	console.log("123456789");
 // 	$("#show_more").unbind();
 // 	$("#show_more").bind("click",function(){
 // 		console.log("more_information");
 // 		$("#mstable2").append(html);
 // 		target.style.display = "block";
 // 	});	
 // }

 // function bindmore_infor(html){
 // 	var target = document.getElementById('trendProfile2');
 // 	$("#show_more1").unbind();
 // 	$("#show_more1").bind("click",function(){
 // 		console.log("more_information");
 // 		$("#mstable2").append(html);
 // 		target.style.display = "block";
 // 	});	
 // }



$(document).ready(function(){
    //获取网络指标
    get_network_infor2();
    //获取最短路径分布
    // getnetwork_line2();
    // drawpicture2(index,value);
    //获取首发者信息
    get_fu_table();
    get_firstuser('timestamp');
    get_pagerank2('all');
    get_tr_table();
    get_trend_maker('content');
    get_trend_pusher('reposts_count');

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

/**
 * This is an example on how to use sigma filters plugin on a real-world graph.
 */
var filter;

/**
 * DOM utility functions
 */
var _ = {
  $: function (id) {
    return document.getElementById(id);
  },

  all: function (selectors) {
    return document.querySelectorAll(selectors);
  },

  removeClass: function(selectors, cssClass) {
    var nodes = document.querySelectorAll(selectors);
    var l = nodes.length;
    for ( i = 0 ; i < l; i++ ) {
      var el = nodes[i];
      // Bootstrap compatibility
      el.className = el.className.replace(cssClass, '');
    }
  },

  addClass: function (selectors, cssClass) {
    var nodes = document.querySelectorAll(selectors);
    var l = nodes.length;
    for ( i = 0 ; i < l; i++ ) {
      var el = nodes[i];
      // Bootstrap compatibility
      if (-1 == el.className.indexOf(cssClass)) {
        el.className += ' ' + cssClass;
      }
    }
  },

  show: function (selectors) {
    this.removeClass(selectors, 'hidden');
  },

  hide: function (selectors) {
    this.addClass(selectors, 'hidden');
  },

  toggle: function (selectors, cssClass) {
    var cssClass = cssClass || "hidden";
    var nodes = document.querySelectorAll(selectors);
    var l = nodes.length;
    for ( i = 0 ; i < l; i++ ) {
      var el = nodes[i];
      //el.style.display = (el.style.display != 'none' ? 'none' : '' );
      // Bootstrap compatibility
      if (-1 !== el.className.indexOf(cssClass)) {
        el.className = el.className.replace(cssClass, '');
      } else {
        el.className += ' ' + cssClass;
      }
    }
  }
};

function get_fu_table(){   
                $.ajax({
                    url: "/identify/table_first_user/?&topic=" + topic + "&start_ts=" + start_ts + "&end_ts=" + end_ts,
                    type: "GET",
                    dataType:"json",
                    success: function(data){
                                                    
                        drawtable(data);
                    }
                });
            }

function drawtable(data){
  var html='';
  var modal_html = '';
  for (var i=0;i<=5;i++){
    row = data[i];
    if (row.length==1){
      continue;
    }
    categorie = row[0]
    html += '<tr><td style="text-align:center"><b>'+categorie+'</b>';
    modal_html += '<tr><td><b>'+categorie+'</b>';
    row_length = row.length;
    for (var j=1; j<=20;j++){
       
      if (j < row_length){
       rrow = row[j];
       uname = rrow[1];
       profile_image_url = row[j][2];
      if (profile_image_url == 'no'){
      profile_image_url = '/static/img/unknown_profile_image.gif';
        }
      }
      else{
        uname = '';
        profile_image_url = '';
      }
      if (j<=9){
        if (uname == ''){
          html += '<td><div class="fu_table_td "  style="width:70px;overflow:hidden;text-overflow: ellipsis;white-space: nowrap;text-align:center"></div></td>';

        }
        else{
          html += '<td><div class="fu_table_td "  style="width:70px;overflow:hidden;text-overflow: ellipsis;white-space: nowrap;text-align:center"><img src=' + profile_image_url + '  title='+uname+'><br>'+'<a>'+uname+'</a></div></td>';
        }

          //html += '<td><div class="fu_table_td "  style="width:70px;overflow:hidden;text-overflow: ellipsis;white-space: nowrap;text-align:center"><img src=' + profile_image_url + '  title='+uname+'><br>'+'<a>'+uname+'</a></div></td>';
      }
      if (uname == ''){
        modal_html += '<td><div class="fu_table_td"  style="width:45px;overflow:hidden;text-overflow: ellipsis;white-space: nowrap;text-align:center"></div></td>';

      }
      else{
        modal_html += '<td><div class="fu_table_td"  style="width:45px;overflow:hidden;text-overflow: ellipsis;white-space: nowrap;text-align:center"><img src=' + profile_image_url + ' title='+uname+'><br>'+'<a>'+uname+'</a></div></td>';

      }
      //modal_html += '<td><div class="fu_table_td"  style="width:45px;overflow:hidden;text-overflow: ellipsis;white-space: nowrap;text-align:center"><img src=' + profile_image_url + ' title='+uname+'><br>'+'<a>'+uname+'</a></div></td>';

  }
    html += '</tr>';
    modal_html += '</tr>';
  }
  $("#alternatecolor").append(html);
  $("#alternate").append(modal_html);
}

function get_tr_table(){
  $.ajax({
    url:'/identify/trend_user/?topic=' + topic + '&start_ts=' + start_ts + '&end_ts=' + end_ts,
    dataType:"json",
    type:"Get",
    async:false,
    success:function(data){
      //console.log('get_tr_table');
      //console.log(data);
      draw_tr_table(data);
    }
  });
}

function draw_tr_table(data){
  var html = '';
  var modal_html = '';
  var l = 20
  for (var i=0;i<2;i++){
    row = data[i];
    categories = row[0]
    html += '<tr><td><b>' + categories + '</b>';
    modal_html += '<tr><td><b>' + categories + '</b>';
    row_length = row.length
    for (var j=1;j<=l;j++){
      if (j<row_length){
      user = row[j];
      //console.log('user');
      //console.log(user);
      uname = user[1];
      profile_image_url = user[2];}
    if (profile_image_url == 'no'){
      profile_image_url = '/static/img/unknown_profile_image.gif';
    }
      if (j<=8){
          html += '<td><div class="fu_table_td "  style="width:70px;overflow:hidden;text-overflow: ellipsis;white-space: nowrap;text-align:center"><img src=' + profile_image_url + '  title='+uname+'><br>'+'<a>'+uname+'</a></div></td>';
         }
      modal_html += '<td><div class="fu_table_td"  style="width:45px;overflow:hidden;text-overflow: ellipsis;white-space: nowrap;text-align:center"><img src=' + profile_image_url + ' title='+uname+'><br>'+'<a>'+uname+'</a></div></td>';
    }
    html += '</tr>';
    modal_html += '</tr>';
  }
  $('#tr_alternatecolor').append(html);
  $('#tr_alternate').append(modal_html);
}

function updatePane2 (graph, filter) {
  // get max degree
  var maxDegree = 0,
      maxPagerank = 0,
      categories = {};
  
  // read nodes
  graph.nodes().forEach(function(n) {
    maxDegree = Math.max(maxDegree, graph.degree(n.id));
    maxPagerank = Math.max(maxPagerank, n.attributes.pagerank);
    
    if(n.attributes.acategory in categories){
        categories[n.attributes.acategory] += 1;
    }
    else{
        categories[n.attributes.acategory] = 1;
    }
  });

  var categoriesSorted = Object.keys(categories).sort(function(a, b){
      return categories[b] - categories[a]
  });
  var categoriesSortedTop10 = categoriesSorted.slice(0, 10);
  
  var cluster_colors = ['#CF0072', '#ED1B24', '#F15A25', '#F8931F', '#FBB03B', '#FDEE21', '#8CC63E', '#009345', '#0171BD', '#2D2F93'];
  var clusterid2color = {};
  for(var i=0; i<cluster_colors.length; i+=1 ){
      clusterid2color[categoriesSortedTop10[i]] = cluster_colors[i];
  }
  function contains(a, obj) {
      for (var i = 0; i < a.length; i++) {
          if (a[i] === obj) {
              return true;
          }
      }
      return false;
  }
  graph.nodes().forEach(function(n) {
      if(contains(categoriesSortedTop10, n.attributes.acategory)){
          n.color = clusterid2color[n.attributes.acategory];
      }
      else{
          n.color = '#11c897';
      }
  });

  // min degree
  _.$('min-degree2').max = maxDegree;
  _.$('max-degree-value2').textContent = maxDegree;

  _.$('min-pagerank2').max = maxPagerank * 100000000;
  _.$('max-pagerank-value2').textContent = maxPagerank * 100000000;
  
  // node category
  var nodecategoryElt = _.$('node-category2');
  // Object.keys(categories).forEach(function(c) {
  categoriesSortedTop10.forEach(function(c) {
    var optionElt = document.createElement("option");
    optionElt.text = c;
    nodecategoryElt.add(optionElt);
  });

  // reset button
  _.$('reset-btn2').addEventListener("click", function(e) {
    
    _.$('min-degree2').value = 0;
    _.$('min-degree-val2').textContent = '0';
    _.$('min-pagerank2').value = 0;
    _.$('min-pagerank-val2').textContent = '0';
    _.$('node-category2').selectedIndex = 0;
    filter.undo().apply();
  });
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

$("input[name='linLogModeRadios']").on("click", function(){
    $('#linLogModeInput2').val($(this).val());
});
$("input[name='outboundAttractionRadios']").on("click", function(){
    $('#outboundAttractionInput2').val($(this).val());
});
$("input[name='adjustSizesRadios']").on("click", function(){
    $('#adjustSizesInput2').val($(this).val());
});
$("input[name='strongGravityModeRadios']").on("click", function(){
    $('#strongGravityModeInput2').val($(this).val());
});

function change_edgeWeightInfluence2(){
    $('#edgeWeightInfluence_span2').html($('#edgeWeightInfluence_input2').val());
}

function change_scalingRatio2(){
    $('#scalingRatio_span2').html($('#scalingRatio_input2').val());
}

function change_gravity2(){
    $('#gravity_span2').html($('#gravity_input2').val());
}

function change_slowdown2(){
    $('#slowdown_span2').html($('#slowdown_input2').val());
}

function network_request_callback2(data) {
    $("#network_progress").removeClass("active");
    $("#network_progress").removeClass("progress-striped");
    networkUpdated2 = 1;

    if (data) {
        $("#loading_network_data2").text("计算完成!");
        $("#sigma-graph2").show();

        sigma.parsers.gexf(data, {
            container: 'sigma-graph2',
            settings: {
                drawEdges: true,
                edgeColor: 'default',
                defaultEdgeColor: '#ccc',
                defaultNodeColor: '#11c897'
            }
        },
            function(s) {
              // Initialize the Filter API
              filter = new sigma.plugins.filter(s);

              updatePane2(s.graph, filter);

              function applyMinDegreeFilter(e) {
                var v = e.target.value;
                _.$('min-degree-val2').textContent = v;

                filter
                  .undo('min-degree2')
                  .nodesBy(function(n) {
                    return this.degree(n.id) >= v;
                  }, 'min-degree2')
                  .apply();
              }

              function applyCategoryFilter(e) {
                var c = e.target[e.target.selectedIndex].value;
                filter
                  .undo('node-category2')
                  .nodesBy(function(n) {
                    return !c.length || n.attributes.acategory === c;
                  }, 'node-category2')
                  .apply();
              }

              function applyMinPagerankFilter(e) {
                var v = e.target.value;
                _.$('min-pagerank-val2').textContent = v;

                filter
                  .undo('min-pagerank2')
                  .nodesBy(function(n) {
                    
                    return n.attributes.pagerank * 100000000 >= v;
                  }, 'min-pagerank2')
                  .apply();
              }
              //过滤器通过固定一种情况，变化另一个情况，但是现在有三种情况怎么做？！
              function applyZhibiaoCategoryFilter(e){
                var v = e.target.value;
                _.$('min-degree2').value = 0;
                _.$('min-degree-val2').textContent = '0';
                _.$('min-pagerank2').value = 0;
                _.$('min-pagerank-val2').textContent = '0';
                _.$('node-category2').selectedIndex = 0;
                filter.undo().apply();
                if(v == 'degree'){
                    $('#min_degree_container2').removeClass('hidden');
                    $('#min_pagerank_container2').addClass('hidden');
                }
                if(v == 'pagerank'){
                    $('#min_pagerank_container2').removeClass('hidden');
                    $('#min_degree_container2').addClass('hidden');
                }
              }

              _.$('min-degree2').addEventListener("input", applyMinDegreeFilter);  // for Chrome and FF
              _.$('min-degree2').addEventListener("change", applyMinDegreeFilter); // for IE10+, that sucks
              _.$('min-pagerank2').addEventListener("input", applyMinPagerankFilter);  // for Chrome and FF
              _.$('min-pagerank2').addEventListener("change", applyMinPagerankFilter); // for IE10+, that sucks
              _.$('zhibiao-category2').addEventListener("change", applyZhibiaoCategoryFilter);
              _.$('node-category2').addEventListener("change", applyCategoryFilter);

              // Start the ForceAtlas2 algorithm:
              var linLogMode = ($('#linLogModeInput2').val() === 'true');
              var outboundAttractionDistribution = ($('#outboundAttractionInput2').val() === 'true');
              var adjustSizes = ($('#adjustSizesInput2').val() === 'true');
              var strongGravityMode = ($('#strongGravityInput').val() === 'true');
              var edgeWeightInfluence = parseInt($('#edgeWeightInfluence_input2').val());
              var scalingRatio = parseInt($('#scalingRatio_input2').val());
              var gravity = parseInt($('#gravity_input2').val());
              var slowDown = parseInt($('#slowdown_input').val());
              var config = {
                  'linLogMode': linLogMode,
                  'outboundAttractionDistribution': outboundAttractionDistribution,
                  'adjustSizes': adjustSizes,
                  'edgeWeightInfluence': edgeWeightInfluence,
                  'scalingRatio': scalingRatio,
                  'strongGravityMode': strongGravityMode,
                  'gravity': gravity,
                  'slowDown': slowDown
              }
              s.startForceAtlas2(config);

              $("#refresh_layout2").click(function(){
                  //s.stopForceAtlas2();
                  var linLogMode = ($('#linLogModeInput2').val() === 'true');
                  var outboundAttractionDistribution = ($('#outboundAttractionInput2').val() === 'true');
                  var adjustSizes = ($('#adjustSizesInput2').val() === 'true');
                  var strongGravityMode = ($('#strongGravityInput').val() === 'true');
                  var edgeWeightInfluence = parseInt($('#edgeWeightInfluence_input2').val());
                  var scalingRatio = parseInt($('#scalingRatio_input2').val());
                  var gravity = parseInt($('#gravity_input2').val());
                  var slowDown = parseInt($('#slowdown_input').val());
                  var config = {
                      'linLogMode': linLogMode,
                      'outboundAttractionDistribution': outboundAttractionDistribution,
                      'adjustSizes': adjustSizes,
                      'edgeWeightInfluence': edgeWeightInfluence,
                      'scalingRatio': scalingRatio,
                      'strongGravityMode': strongGravityMode,
                      'gravity': gravity,
                      'slowDown': slowDown
                  }
                  s.configForceAtlas2(config);
                  s.startForceAtlas2();
                  s.refresh();
              });

              $("#pause_layout2").click(function(){
                  s.stopForceAtlas2();
              });

              $("#stop_layout2").click(function(){
                  s.killForceAtlas2();
              });

              /*
              $('#community_detail_a').click(function(){
                  var community_id = $('#community').html();
                  var community_nodes = [];
                  s.graph.nodes().forEach(function(n) {
                      if(String(n.attributes.acategory) == String(community_id)){
                          community_nodes.push(n);
                      }
                  });
                  community_nodes.sort(function(a, b){
                      return parseFloat(a.attributes.pagerank) - parseFloat(b.attributes.pagerank)
                  });
                  var top_nodes = community_nodes.slice(community_nodes.length-3, community_nodes.length);
                  top_nodes.reverse();
                  refresh_important_nodes(top_nodes);
              });

              function refresh_important_nodes(nodes){
                  $("#group_user_list").empty();
                  var html = "";
                  for(var n in nodes){
                      console.log(n);
                      $("#group_user_list").append("<span>" + n.attributes.name + "(" + n.attributes.pagerank + ")于" + n.attributes.timestamp + " 发布 " + n.attributes.text + "</span>");
                  }
              }
              
              $('#neighbourhood_detail_a').click(function(){
                  var community_id = $('#community').val();
                  var community_nodes = [];
                  s.graph.nodes().forEach(function(n) {
                      if(n.attributes.acategory == parseInt(community_id)){
                          community_nodes.push(n);
                      }
                  });
              });
              */

                // We first need to save the original colors of our
                // nodes and edges, like this:
                s.graph.nodes().forEach(function(n) {
                  n.originalColor = n.color;
                });
                s.graph.edges().forEach(function(e) {
                  e.originalColor = e.color;
                  // console.log('e.originalColor');
                  // console.log(e.originalColor);
                  // console.log(e);
                });

                // When a node is clicked, we check for each node
                // if it is a neighbor of the clicked one. If not,
                // we set its color as grey, and else, it takes its
                // original color.
                // We do the same for the edges, and we only keep
                // edges that have both extremities colored.
                s.bind('clickNode', function(e) {
                  var nodeId = e.data.node.id,
                      neighbor_graph = s.graph.neighborhood(nodeId),
                      toKeep = {},
                      node = e.data.node;

                  var node_uid = node.label;
                  var node_name = node.attributes.name;
                  var node_location = node.attributes.location;
                  var node_pagerank = node.attributes.pagerank;
                  var node_community = node.attributes.acategory;
                  var node_text = node.attributes.text;
                  var node_reposts_count = node.attributes.reposts_count;
                  var node_comments_count = node.attributes.comments_count;
                  var node_timestamp = node.attributes.timestamp;
                  var node_rank_pr = node.attributes.rank_pr;
                  var graph_type = 2;

                  $('#nickname2').html('<a target="_blank" href="http://weibo.com/u/' + node_uid + '">' + node_name + '</a>');
                  $('#location2').html(node_location);
                  $('#pagerank2').html(new Number(node_pagerank).toExponential(2) + ' ( 排名:' + node_rank_pr + ' )');
                  
                  //$('#weibo_created_at').html(node_timestamp);
                  //$('#weibo_text').html(node_text);
                  //$('#weibo_reposts_count').html(node_reposts_count);
                  //$('#weibo_comments_count').html(node_comments_count);
                  //$('#community2').html(node_community);
                  //$('#user_weibo2').html('<a target="_blank" href="/index/user_weibo/?uid=' + node_uid + '">' + '查看用户微博列表' + '</a>');
                  $('#community_detail_a2').html('<button onclick="network_uid_community(' + node_community +','+ node_uid + ',' + graph_type +')">' + '社团' + '</button>');
                  $('#user_weibo2').html('<button onclick="network_weibolist(' + node_uid + ',' + graph_type +')">' + '微博' + '</button>');
                  $('#neighbourhood_detail_a2').html('<button onclick="network_uid_neighbor(' + node_uid + ',' + graph_type +')">' + '邻居' + '</button>');
                  
                  neighbor_graph.nodes.forEach(function(n){
                      toKeep[n.id] = n; 
                  });
                  toKeep[nodeId] = e.data.node;

                  s.graph.nodes().forEach(function(n) {
                    if (toKeep[n.id])
                      n.color = n.originalColor;
                    else
                      n.color = '#eee';
                  });

                  s.graph.edges().forEach(function(e) {
                    if (toKeep[e.source] && toKeep[e.target])
                      e.color = e.originalColor;
                    else
                      e.color = '#eee';
                  });

                  // Since the data has been modified, we need to
                  // call the refresh method to make the colors
                  // update effective.
                  s.refresh();
                });

                // When the stage is clicked, we just color each
                // node and edge with its original color.
                s.bind('clickStage', function(e) {
                  s.graph.nodes().forEach(function(n) {
                    n.color = n.originalColor;
                  });

                  s.graph.edges().forEach(function(e) {
                    e.color = e.originalColor;
                  });

                  // Same as in the previous event:
                  s.refresh();
                });
        });
    }

    else {
        $("#loading_network_data2").text("暂无结果!");
    }

}


//节点信息部分用户微博列表数据获取
function network_weibolist(uid, network_type){
  if (network_type==1){
    network_type = 'source_graph';
  }
  else if(network_type==2){
    network_type = 'direct_superior_graph';
  }
  console.log('network_weibolist');
  console.log(network_type);
  $.ajax({
    url: "/identify/uid_weibo/?uid=" + uid + "&topic="+ topic + '&start_ts=' + start_ts + '&end_ts=' + end_ts,
    dataType: "json",
    type:'Get',
    async:false,
    success:function(data){
      console.log(data);
      show_network_weibo(data, network_type);

    }
  });
}


//显示节点信息部分的微博列表
function show_network_weibo(data, network_type){
  console.log('show_network_weibo');
  console.log(network_type);
  if (network_type=='direct_superior_graph'){
  document.getElementById("network_uid_community").style.display="none";
  document.getElementById("network_uid_neighbor").style.display="none";
  document.getElementById("network_uid2weibo").style.display = "";
  $("#network_weibo_ul").empty();
  var pre_div_id = 'network_weibo_ul';
  var pre_div_id2 = 'network_content_control_height';
  }
  else if(network_type=='source_graph'){
    document.getElementById('network_uid_community1').style.display='none';
    document.getElementById('network_uid_neighbor1').style.display='none';
    document.getElementById('network_uid2weibo1').style.display='';
    $('#network_weibo_ul1').empty();
    var pre_div_id = 'network_weibo_ul1';
    var pre_div_id2 = 'network_content_control_height1';
  }

  
  var html = "";
  var n = data.length;
  for(var i=0;i<n;i++){
    var weibo = data[i]
    var wid = weibo[0];
    var uid = weibo[1];
    var name = weibo[2];
    var location = weibo[3]
    var friends_count = weibo[4];
    var followers_count = weibo[5];
    var created_at = weibo[6];
    var statuses_count = weibo[7];
    var profile_image_url = weibo[8];
    if (profile_image_url == 'no'){
      profile_image_url = '/static/img/unknown_profile_image.gif';
    }
    var date = weibo[9];
    var text = weibo[10];
    var geo = weibo[11];
    if (geo==null){
       geo = '未知';
    }
    var source = weibo[12];
    var reposts_count = weibo[13];
    var comments_count = weibo[14];
    var weibo_link = weibo[15];
    var user_link = 'http://weibo.com/u/' + uid;
    var repost_tree_link = 'http://219.224.135.60:8080/show_graph/' + wid;
    html += '<li class="item"><div class="weibo_face"><a target="_blank" href="' + user_link + '">';
    html += '<img src="' + profile_image_url + '">';
    html += '</a></div>';
    html += '<div class="weibo_detail">';
    html += '<p>昵称:<a class="undlin" target="_blank" href="' + user_link  + '">' + name + '</a>(' + location + ')&nbsp;&nbsp;发布ip:' + '未知' + '&nbsp;&nbsp;发布内容：&nbsp;&nbsp;' + text + '</p>';
    html += '<div class="weibo_info">';
    html += '<div class="weibo_pz">';
    html += '<a class="undlin" href="javascript:;" target="_blank">转发数(' + reposts_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
    html += '<a class="undlin" href="javascript:;" target="_blank">评论数(' + comments_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
    html += '<a class="undlin" href="javascript:;" target="_blank">粉丝数(' + friends_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
    html += '<a class="undlin" href="javascript:;" target="_blank">关注数(' + followers_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
    html += '<a class="undlin" href="javascript:;" target="_blank">微博数(' + statuses_count + ')</a></div>';
    html += '<div class="m">';
    html += '<a class="undlin" target="_blank" href="' + weibo_link + '">' + date + '</a>&nbsp;-&nbsp;';
    //html += '<a target="_blank" href="http://weibo.com">新浪微博</a>&nbsp;-&nbsp;';
    html += '<a target="_blank" href="' + weibo_link + '">微博</a>&nbsp;-&nbsp;';
    html += '<a target="_blank" href="' + user_link + '">用户</a>&nbsp;-&nbsp;';
    html += '<a target="_blank" href="' + '#huaxiang' + '">画像</a>&nbsp;-&nbsp;';
    html += '<a target="_blank" href="' + repost_tree_link + '">转发树</a>';
    html += '</div>'
    html += '</div>'
    html += '</div>'
    html += '</li>' 
  }
   $("#"+pre_div_id).append(html);
   $("#"+pre_div_id).css("height", $("#weibo_ul").css("height"));
}

//获取节点邻居信息
function network_uid_neighbor(uid, network_type){
  if (network_type==1){
    network_type = 'source_graph';
  }
  else if(network_type==2){
    network_type = 'direct_superior_graph';
  }
  console.log('network_uid_neighbor');
  console.log(network_type);
  $.ajax({
    url: "/identify/uid_neighbor/?uid=" + uid + "&topic="+ topic + '&start_ts=' + start_ts + '&end_ts=' + end_ts + '&network_type=' + network_type,
    dataType: "json",
    type:'Get',
    async:false,
    success:function(data){
      console.log(data);
      show_network_neighbor(data, network_type);
    }
  });

}

function network_uid_community(cid, uid, network_type){
  
  if (network_type==1){
    network_type = 'source_graph';
  }
  else if(network_type==2){
    network_type = 'direct_superior_graph';
  }
  console.log('network_uid_community');
  console.log(network_type);
  $.ajax({
    url:"/identify/uid_community/?uid=" + uid + '&topic=' + topic + '&start_ts=' + start_ts + '&end_ts=' + end_ts + '&network_type=' + network_type + '&community_id=' + cid,
    dataType:'json',
    type:'Get',
    async:false,
    success:function(data){
      //console.log(data);
      show_network_community(data, network_type);
    } 
  });

}
//显示节点所属社区信息
function show_network_community(data, network_type){
  if (network_type=='direct_superior_graph'){
  document.getElementById("network_uid_community").style.display="";
  document.getElementById("network_uid_neighbor").style.display="none";
  document.getElementById("network_uid2weibo").style.display = "none";
  }
  else if(network_type=='source_graph'){
    document.getElementById('network_uid_community1').style.display='';
    document.getElementById('network_uid_neighbor1').style.display='none';
    document.getElementById('network_uid2weibo1').style.display='none';
  }
  weibos = data[0];
  neighbor_weibo(weibos, 'community', network_type);
  top_words = data[1];
  draw_neighbor_cloud(top_words, 'community', network_type);
  sentiment = data[2];
  draw_neighbor_pie(sentiment, 'community', network_type);
  users = data[3];
  draw_user_table(users, 'community', network_type);
  trend = data[4];
  //console.log('trend');
  //console.log(trend);
  draw_trend(trend, 'community', network_type)
  user_num = users.length;
  weibo_num = weibos.length;
  //console.log(user_num);
  //console.log(weibo_num);
  draw_easy_info(user_num, weibo_num, 'community', network_type);
}

function draw_easy_info(u_num, w_num, type, network_type){
  if (type=='community' && network_type=='direct_superior_graph'){
    pre_div_id = 'community_easy_info';
    type_ch = '社区';
  }
  else if (type=='neighbor' && network_type=='direct_superior_graph'){
    pre_div_id = 'neighbor_easy_info';
    type_ch = '邻居'; 
  }
  else if (type=='community' && network_type=='source_graph'){
    pre_div_id = 'community_easy_info1';
    type_ch = '社区';
  }
  else if (type=='neighbor' && network_type=='source_graph'){
    pre_div_id = 'neighbor_easy_info1';
    type_ch = '邻居';
  }
  $('#'+pre_div_id).empty();
  html = ''; 
  html += '<a style="margin-left:20px;font-size:13px;">' + type_ch + '用户数:' + u_num + '</a>&nbsp&nbsp<a style="margin-left:20px;font-size:13px;">' + type_ch + '微博数:' + w_num + '</a>';
  $('#'+pre_div_id).append(html);
}

//显示节点邻居信息
function show_network_neighbor(data, network_type){
  if (network_type=='direct_superior_graph'){
  document.getElementById("network_uid_community").style.display="none";
  document.getElementById("network_uid_neighbor").style.display="";
  document.getElementById("network_uid2weibo").style.display = "none";
  }
  else if(network_type == 'source_graph'){
  document.getElementById('network_uid_community1').style.display='none';
  document.getElementById('network_uid_neighbor1').style.display='';
  document.getElementById('network_uid2weibo1').style.display='none';
  }
  weibos = data[0];
  neighbor_weibo(weibos, 'neighbor', network_type);
  top_words = data[1];
  draw_neighbor_cloud(top_words, 'neighbor', network_type);
  sentiment = data[2];
  draw_neighbor_pie(sentiment, 'neighbor', network_type);
  users = data[3];
  draw_user_table(users, 'neighbor', network_type);
  trend = data[4];
  draw_trend(trend, 'neighbor', network_type);
  user_num = users.length;
  weibo_num = weibos.length;
  //console.log(user_num);
  //console.log(weibo_num);
  draw_easy_info(user_num, weibo_num, 'neighbor', network_type);

}

// 显示节点信息所在的社区或者邻居的名单列表
function draw_user_table(data, type, network_type){
  if (type=='neighbor' && network_type=='direct_superior_graph'){
    pre_div_id1 = 'neighbor_alternatecolor';
  }
  else if(type=='community' && network_type=='direct_superior_graph'){
    pre_div_id1 = 'community_alternatecolor';
  }
  else if(type=='neighbor' && network_type=='source_graph'){
    pre_div_id1 = 'neighbor_alternatecolor1';
  }
  else if (type=='community' && network_type=='source_graph'){
    pre_div_id1 = 'community_alternatecolor1';
  }
  $('#'+pre_div_id1).empty();
  N = data.length;

  cellCount = N / 7;
  if (N - cellCount * 7 != 0){
    cellCount += 1;
  }
  draw_profile(cellCount/2,data,pre_div_id1);

  $("#more_profile").click(function(){
  N = data.length;

  cellCount = N / 7;
  if (N - cellCount * 7 != 0){
    cellCount += 1;
  }
  draw_profile(cellCount,data,pre_div_id1);
});

  $("#more_profile1").click(function(){
  N = data.length;

  cellCount = N / 7;
  if (N - cellCount * 7 != 0){
    cellCount += 1;
  }
  draw_profile(cellCount,data,pre_div_id1);
});

  $("#more_profile2").click(function(){
  N = data.length;

  cellCount = N / 7;
  if (N - cellCount * 7 != 0){
    cellCount += 1;
  }
  draw_profile(cellCount,data,pre_div_id1);
});

  $("#more_profile3").click(function(){
  N = data.length;

  cellCount = N / 7;
  if (N - cellCount * 7 != 0){
    cellCount += 1;
  }
  draw_profile(cellCount,data,pre_div_id1);
});

}

  function draw_profile(cellCount,data,pre_div_id1){
  $('#'+pre_div_id1).empty();
  var html = '';
  for (var i=0;i<cellCount;i++){
    html += '<tr>'
    for (var j=1;j<=7;j++){
      var index = i * 7 + (j-1);
      if (index < N){
      user = data[index];
      //console.log(user);
      uid = user[0];
      uname = user[1];
      profile_image_url = user[2];
    if (profile_image_url == 'no'){
      profile_image_url = '/static/img/unknown_profile_image.gif';
    }
      user_link = 'http://weibo.com/u/' + uid;
      user_sys_link = '#' + uid; 
      html += '<td><div class="tr_table_td" style="width:70px;overflow:hidden;text-overflow: ellipsis;white-space: nowrap;text-align:center"><img src=' + profile_image_url + '  title='+uname+'><br>';
      html += '<a>' + uname +'</a><br><a target="_blank"style= "font-size:10px" href="' + user_link + '">用户</a>&nbsp;&nbsp';
      html += '<a target="_blank" style= "font-size:10px" href="' + user_sys_link + '">画像</a></div>';
    }       
  }
    html += '</tr>';
  }
  $('#'+pre_div_id1).append(html);
  console.log(pre_div_id1);
}

function draw_trend(data, type, network_type){
  //console.log('draw_trend');
  var xAxisTitleText = '时间';
  var yAxisTitleText = '数量';
  var series_data = [{
            name: '全量',
            data: [],
            id: 'total',
            color: '#b172c5',
            marker : {
                enabled : false,
            }
        }];
  console.log('draw_trend_before');
  console.log(type);
  if (type=='neighbor' && network_type=='direct_superior_graph'){
    var name = '邻居微博趋势';
    var trend_div_id = 'trend_div_whole';

  }
  else if(type=='community' && network_type=='direct_superior_graph'){
    var name = '社区微博趋势';
    var trend_div_id = 'community_trend_div_whole';
  }
  else if (type=='neighbor' && network_type=='source_graph'){
    var name = '邻居微博趋势';
    var trend_div_id = 'trend_div_whole1';
  }
  else if (type=='community' && network_type=='source_graph'){
    var name = '社区微博趋势';
    var trend_div_id = 'community_trend_div_whole1';
  }
  console.log('draw_trend');
  console.log(type);
  console.log(network_type);
  console.log(trend_div_id);
  var timestamp_list = [];
  var count_list = [];
  var data_list = [];
  for (var i=0;i<data.length;i++){
      var row = data[i];
      timestamp_list.push(row[0]*1000);
      count_list.push([row[1]]);
      data_list.push([row[0]*1000, row[1]]);
  }
  console.log('timestamp_list');
  console.log(timestamp_list);
  //console.log('count_list');
  //console.log(count_list);
  $('#' + trend_div_id).highcharts({
    chart: {
            type: 'spline',// line,
            animation: Highcharts.svg, // don't animate in old IE
            style: {
                fontSize: '12px',
                fontFamily: 'Microsoft YaHei'
            }},
    title : {
            text: '走势分析图', // trends_title
            margin: 20,
            style: {
                color: '#666',
                fontWeight: 'bold',
                fontSize: '14px',
                fontFamily: 'Microsoft YaHei'
            }
        },
    lang: {
            printChart: "打印",
            downloadJPEG: "下载JPEG 图片",
            downloadPDF: "下载PDF文档",
            downloadPNG: "下载PNG 图片",
            downloadSVG: "下载SVG 矢量图",
            exportButtonTitle: "导出图片"
        },
    xAxis: {
            title: {
                enabled: true,
                text: xAxisTitleText,
                style: {
                    color: '#666',
                    fontWeight: 'bold',
                    fontSize: '12px',
                    fontFamily: 'Microsoft YaHei'
                }

            },
            type: 'datetime',
            tickPixelInterval: 150,
            //categories:timestamp_list,
            // labels:{
            //   step: 24
            // }
        },

    yAxis: {
            min: 0,
            title: {
                enabled: true,
                text: yAxisTitleText,
                style: {
                    color: '#666',
                    fontWeight: 'bold',
                    fontSize: '12px',
                    fontFamily: 'Microsoft YaHei'
                }
            },

        },
         plotOptions: {
          spline: {
              lineWidth: 2,
              states: {
                  hover: {
                      lineWidth: 3
                  }
              },
              marker: {
                  enabled: false
              },
            }
        },
    tooltip: {
            valueDecimals: 2,
            xDateFormat: '%Y-%m-%d %H:%M:%S'
        },

    legend: {
            layout: 'horizontal',
            //verticalAlign: true,
            //floating: true,
            align: 'center',
            verticalAlign: 'bottom',
            x: 0,
            y: -2,
            borderWidth: 1,
            itemStyle: {
                color: '#666',
                fontWeight: 'bold',
                fontSize: '12px',
                fontFamily: 'Microsoft YaHei'
            }
            //enabled: true,
            //itemHiddenStyle: {
                //color: 'white'
            //}
        },
    exporting: {
            enabled: true
        },
    series: [{
            name: '数量',
            data: data_list
        }]
  });
}

function draw_neighbor_pie(data, type, network_type){
  var pie_title = '类别饼图';
  var pie_series_title = '各类占比';
  if (type=='neighbor' && network_type=='direct_superior_graph'){
    var pie_div_id = 'pie_div';
  }
  else if(type=='community' && network_type=='direct_superior_graph'){
    var pie_div_id = 'community_pie_div';
  }
  else if(type=='neighbor' && network_type=='source_graph'){
    var pie_div_id = 'pie_div1';
  }
  else if (type=='community' && network_type=='source_graph'){
    var pie_div_id = 'community_pie_div1';
  }
  var pie_data = [];
  var legend_data = [];
  for (var i=0;i<data.length;i++){
    var row = data[i];
    sentiment = row[0];
    count = row[1];
    pie_data.push({
                value: count,
                name: sentiment
            });
    legend_data.push(sentiment);
  }
  var option = {
        backgroundColor: '#FFF',
        color: ['#11c897', '#fa7256', '#6e87d7', '#b172c5'],
        title : {
            text: pie_title,
            x: 'center',
            textStyle:{
                fontWeight: 'lighter',
                fontSize: 13
            }
        },
        toolbox: {
            show: true,
            feature : {
                mark : {show: true},
                dataView : {show: true, readOnly: false},
                //magicType : {show: true, type: ['line', 'bar']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        tooltip: {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)",
            textStyle: {
                fontWeight: 'bold',
                fontFamily: 'Microsoft YaHei'
            }
        },
        legend: {
            orient:'vertical',
            x : 'left',
            data: legend_data,
            textStyle: {
                fontWeight: 'bold',
                fontFamily: 'Microsoft YaHei'
            }
        },

        calculable : true,
        series : [
            {
                name: pie_series_title,
                type: 'pie',
                radius : '50%',
                center: ['50%', '60%'],
                itemStyle: {
                    normal: {
                        label: {
                            position: 'inner',
                            formatter: "{d}%",
                            textStyle: {
                                fontWeight: 'bold',
                                fontFamily: 'Microsoft YaHei'
                            }
                        },
                        labelLine: {
                            show: false
                        }
                    },
                    emphasis: {
                        label: {
                            show: true,
                            formatter: "{b}\n{d}%",
                            textStyle: {
                                fontWeight: 'bold',
                                fontFamily: 'Microsoft YaHei'
                            }
                        }
                    }
                },
                data: pie_data
            }
        ],
        textStyle: {
            fontWeight: 'bold',
            fontFamily: 'Microsoft YaHei'
        }
    };

    var myChart = echarts.init(document.getElementById(pie_div_id));
    myChart.setOption(option);

}

function draw_neighbor_cloud(data, type, network_type){
  var max_keywords_size = 20;
  var min_keywords_size = 5;
  //console.log('keyword');
  //console.log(data);
  var div_id_cloud = '' ;
  // console.log('draw_neighbor_cloud---network_type');
  // console.log(network_type);
  if (type=="neighbor" && network_type=='direct_superior_graph'){
    div_id_cloud = 'keywords_cloud_div';
  }
  else if (type=='community' && network_type=='direct_superior_graph'){
    div_id_cloud = 'community_keywords_cloud_div';
  }
  else if(type=='neighbor' && network_type=='source_graph'){
    div_id_cloud = 'keywords_cloud_div1';
  }
  else if (type=='community' && network_type =='source_graph'){
    div_id_cloud = 'community_keywords_cloud_div1';
  }
  $('#'+div_id_cloud).empty();
  if (data==[]){
    $('#'+div_id_cloud).append("<a style='font-size:1ex'>关键词云数据为空</a>");
  }
  else{
    var min_count, max_count = 0, words_count_obj = {};
    for (var i=0;i<data.length; i++){
      var keyword = data[i];
      //console.log(keyword);
      var word = keyword[0];
      var count = keyword[1];
      //console.log(word);
      //console.log(count);
      if(count > max_count){
                max_count = count;
            }
      if(!min_count){
                min_count = count;
            }
      if(count < min_count){
                min_count = count;
            }
      words_count_obj[word] = count;


    }
    //console.log(words_count_obj);
    var color = '#11c897';
    for(var keyword in words_count_obj){
        var count = words_count_obj[keyword];
        var size = defscale(count, min_count, max_count, min_keywords_size, max_keywords_size);
        $('#'+div_id_cloud).append('<a><font style="color:' + color +  '; font-size:' + size + 'px;">' + keyword + '</font></a>');
    }
    console.log(div_id_cloud);

    on_load(div_id_cloud);

  }
}
// 根据权重决定字体大小
function defscale(count, mincount, maxcount, minsize, maxsize){
    if(maxcount == mincount){
        return (maxsize + minsize) * 1.0 / 2
    }else{
        return minsize + 1.0 * (maxsize - minsize) * Math.pow((count / (maxcount - mincount)), 2)
    }
}

function neighbor_weibo(data, type, network_type){
  if (type=='neighbor' && network_type =='direct_superior_graph'){
    var div_id = 'neighbor_weibo_ul';
    var div_id2 = 'neighbor_content_control_height';
  }
  else if (type=='neighbor' && network_type=='source_graph'){
    var div_id = 'neighbor_weibo_ul1';
    var div_id2 = 'neighbor_content_control_height1';

  }
  else if(type=='community' && network_type == 'direct_superior_graph'){
    var div_id = 'community_weibo_ul';
    var div_id2 = 'community_content_control_height';
  }
  else if(type=='community' && network_type == 'source_graph'){
    var div_id = 'community_weibo_ul1';
    var div_id2 = 'community_content_control_height1';
  }
  $("#"+div_id).empty();
  N = 5;
  if (N >= data.length){
  N = data.length;}
  draw_text(N,data,div_id,div_id2);
    $("#more_inform").click(function(){
  N = 20;
  draw_text(N,data,div_id,div_id2);

});
    $("#more_inform1").click(function(){
  N = 20;
  draw_text(N,data,div_id,div_id2);
});

  $("#more_inform2").click(function(){
  N = 20;
  draw_text(N,data,div_id,div_id2);

});
    $("#more_inform3").click(function(){
  N = 20;
  draw_text(N,data,div_id,div_id2);
});
}
function  draw_text(N,data,div_id,div_id2){
     var html = '';
    $("#"+div_id).empty();
  for (var i = 0; i < N; i += 1){
    var weibo = data[i];
    var mid = weibo[0];
    var name = weibo[1];
    var location = weibo[2];
    var friends_count = weibo[3];
    var followers_count = weibo[4];
    var created_at = weibo[5];
    var statuses_count = weibo[6];
    var profile_image_url = weibo[7];
    if (profile_image_url == 'no'){
      profile_image_url = '/static/img/unknown_profile_image.gif';
    }
    var text = weibo[8];
    var date = weibo[9];
    var reposts_count = weibo[10];
    var source = weibo[11];
    var geo = weibo[12];
    if (geo==null){
      geo = '未知';
    }
    var comments_count = weibo[13];
    var sentiment = weibo[14];
    var weibo_link = weibo[15];
    var uid = weibo[16]
    var rank = i + 1;
    var user_link = 'http://weibo.com/u/' + uid;
    var repost_tree_link = 'http://219.224.135.60:8080/show_graph/' + mid;

    html += '<li class="item"><div class="weibo_face"><a target="_blank" href="' + user_link + '">';
    html += '<img src="' + profile_image_url + '">';
    html += '</a></div>';
    html += '<div class="weibo_detail">';
    html += '<p>排名:'+rank+'&nbsp;&nbsp;昵称:<a class="undlin" target="_blank" href="' + user_link  + '">' + name + '</a>&nbsp;&nbsp;(' + location + ')&nbsp;&nbsp;发布ip:' + geo + '&nbsp;&nbsp;发布内容:&nbsp;&nbsp;' + text + '</p>';
    html += '<div class="weibo_info">';
    html += '<div class="weibo_pz">';
    html += '<a class="undlin" href="javascript:;" target="_blank">转发数(' + reposts_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
    html += '<a class="undlin" href="javascript:;" target="_blank">评论数(' + comments_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
    html += '<a class="undlin" href="javascript:;" target="_blank">粉丝数(' + friends_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
    html += '<a class="undlin" href="javascript:;" target="_blank">关注数(' + followers_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
    html += '<a class="undlin" href="javascript:;" target="_blank">微博数(' + statuses_count + ')</a></div>';
    html += '<div class="m">';
    html += '<a class="undlin" target="_blank" href="' + weibo_link + '">' + date + '</a>&nbsp;-&nbsp;';
    html += '<a target="_blank" href="' + weibo_link + '">微博</a>&nbsp;-&nbsp;';
    html += '<a target="_blank" href="' + user_link + '">用户</a>&nbsp;-&nbsp;';
    html += '<a target="_blank" href="#">画像</a>&nbsp;-&nbsp;';
    html += '<a target="_blank" href="' + repost_tree_link + '">转发树</a>';
    html += '</div>'
    html += '</div>'
    html += '</div>'
    html += '</li>' 
  }
   $("#"+div_id).append(html);
  $("#content_control_height").css("height", $("#weibo_ul").css("height"));

}


//click生成网络的入口
function show_network2() {
    networkShowed = 0;
    network_type3 = 'direct_superior_graph'
    
    if (!networkShowed) {
        $("#network2").height(610);
        //$("#loading_network_data9").css("display", "block");
        $('#loading_network_data9').text('计算完成');
        $("#network2").removeClass('out');
        $("#network2").addClass('in');
        networkShowed = 0;
        if (!networkUpdated2){
            $.ajax({
                url: "/identify/graph/?topic=" + topic +'&start_ts=' + start_ts +'&end_ts='+end_ts+'&network_type='+network_type3,
                dataType: "xml",
                type: "GET",
                async: false,

                success: function (data) {
                    networkdata = data;
                    //console.log('network_data');
                    //console.log(data);
                    network_request_callback2(data);
                },
                error: function(result) {
                    $("#loading_network_data9").text("暂无结果!");
                }
            })
        }
   }
 else {
          networkShowed = 0;
          $("#network2").removeClass('in');
           $("#network2").addClass('out');
 }
}

function fu_request_callback(data){
  rankdata = data;
  var status = 'current finished';
  var page_num = 10 ;
  if (status == 'current finished'){
    $("#current_process_bar").css('width', "100%")
    $("#current_process").removeClass("active");
    $("#current_process").removeClass("progress-striped");
    fu_current_data = data;
   
    if (fu_current_data.length) {
      $("#loading_current_data1").text("计算完成!");
      if (fu_current_data.length < page_num) {
          page_num = fu_current_data.length
          create_firstuser_table(fu_current_data, 0, page_num, 'pro');
      }
      else {
          create_firstuser_table(fu_current_data, 0, page_num, 'pro');
          var total_pages = 0;
          if (fu_current_data.length % page_num == 0) {
              total_pages = fu_current_data.length / page_num;
          }
          else {
              total_pages = fu_current_data.length / page_num + 1;
          }
  
          $('#rank_page_selection2').bootpag({
              total: total_pages,
              page: 1,
              maxVisible: 30
          }).on("page", function(event, num){
              start_row = (num - 1)* page_num;
              end_row = start_row + page_num;
              if (end_row > fu_current_data.length)
                  end_row = fu_current_data.length;
                  create_firstuser_table(fu_current_data, start_row, end_row, 'pro');
          });
      }
  }
  else {
      $("#loading_current_data1").text("很抱歉，本期计算结果为空!");
  }
  }
  else{
    return
  }

}

function fu_ul_request_callback(data,start_row,end_row){
  $("#firstuser_ul").empty();
  if (data.length){
   $("#loading_current_data1").text("计算完成!");
  }
  
  var html = "";
  //注意这里的翻页还要做处理
    N=data.length;
   
   for(var i = start_row; i < end_row; i += 1){
    var firstuser_item = data[i]
    var rank = firstuser_item[0]
    var uid = firstuser_item[1]
    var uname = firstuser_item[2]
    var location = firstuser_item[3]
    var domain = firstuser_item[4]
    var timestamp = firstuser_item[5]
    var text = firstuser_item[6]
    var profile_image_url = firstuser_item[7]
    if (profile_image_url == 'no'){
      profile_image_url = '/static/img/unknown_profile_image.gif';
    }
    var friends_count = firstuser_item[8]
    var followers_count = firstuser_item[9]
    var statuses_count = firstuser_item[10]
    var created_at = firstuser_item[11]
    var geo = firstuser_item[12]
    if (geo==null){
      geo = '未知';
    }
    var source = firstuser_item[13]
    var weibo_link = firstuser_item[14]
    var mid = firstuser_item[15]
    var user_link = 'http://weibo.com/u/' + uid;
    var repost_tree_link = 'http://219.224.135.60:8080/show_graph/' + mid;
    html += '<li class="item"><div class="weibo_face"><a target="_blank" href="' + user_link + '">';
    html += '<img src="' + profile_image_url + '">';
    html += '</a></div>';
    html += '<div class="weibo_detail">';
    html += '<p>排名:'+rank+'&nbsp;&nbsp;昵称:<a class="undlin" target="_blank" href="' + user_link  + '">' + uname + '</a>&nbsp;&nbsp;(' + location + ')&nbsp;&nbsp;领域:' + domain + '&nbsp;&nbsp;发布ip:' + geo + '&nbsp;&nbsp;发布内容:&nbsp;&nbsp;' + text + '</p>';
    html += '<div class="weibo_info">';
    html += '<div class="weibo_pz">';
    html += '<a class="undlin" href="javascript:;" target="_blank">粉丝数(' + friends_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
    html += '<a class="undlin" href="javascript:;" target="_blank">关注数(' + followers_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
    html += '<a class="undlin" href="javascript:;" target="_blank">微博数(' + statuses_count + ')</a></div>';
    html += '<div class="m">';
    html += '<a class="undlin" target="_blank" href="' + weibo_link + '">' + timestamp + '</a>&nbsp;-&nbsp;';
    html += '<a target="_blank" href="' + weibo_link + '">微博</a>&nbsp;-&nbsp;';
    html += '<a target="_blank" href="' + user_link + '">用户</a>&nbsp;-&nbsp;';
      html += '<a target="_blank" href="#">画像</a>&nbsp;-&nbsp;';
    html += '<a target="_blank" href="' + repost_tree_link + '">转发树</a>';
    html += '</div>'
    html += '</div>'
    html += '</div>'
    html += '</li>'
   } 
   $("#firstuser_ul").append(html);
   $("#content_control_height").css("height", $("#weibo_ul").css("height"));
   firstuser_more(data,start_row, end_row);
}

function firstuser_more(data,start_row,end_row){
	var start = start_row;
	var end = data.length;
	$("#firstuser_more").unbind();
	$("#firstuser_more").bind("click",function(){
		fu_ul_request_callback(data,start,end);
		//$("#more_info").empty();
	});
}

function trendmaker_more(data,start_row,end_row){
	var start = start_row;
	var end = data.length;
	$("#trendmaker_more").unbind();
	$("#trendmaker_more").bind("click",function(){
		tr_maker_request_callback(data,start,end);
		//$("#more_info").empty();
	});
}

function trendpusher_more(data,start_row,end_row){
	var start = start_row;
	var end = data.length;
	$("#trendpusher_more").unbind();
	$("#trendpusher_more").bind("click",function(){
		console.log("123456");
		tr_pusher_request_callback(data,start,end);
		//$("#more_info").empty();
	});
}

function tr_maker_request_callback(data,start_row,end_row){
  $("#trend_maker_ul").empty();
  if (data.length){
   $("#loading_current_data4").text("计算完成!");
  }
  
  var html = "";
  //注意这里的翻页还要做处理
    N=data.length;
   
   for(var i = start_row; i < end_row; i += 1){
    var firstuser_item = data[i]
    var rank = firstuser_item[0]
    var uid = firstuser_item[1]
    var uname = firstuser_item[2]
    var location = firstuser_item[3]
    var domain = firstuser_item[4]
    var timestamp = firstuser_item[5]
    var text = firstuser_item[6]
    var profile_image_url = firstuser_item[7]
    if (profile_image_url == 'no'){
      profile_image_url = '/static/img/unknown_profile_image.gif';
    }
    var friends_count = firstuser_item[8]
    var followers_count = firstuser_item[9]
    var statuses_count = firstuser_item[10]
    var created_at = firstuser_item[11]
    var geo = firstuser_item[12]
    if (geo==null){
      geo = '未知';
    }
    var source = firstuser_item[13]
    var weibo_link = firstuser_item[14]
    var mid = firstuser_item[15]
    var reposts_count = firstuser_item[16]
    var user_link = 'http://weibo.com/u/' + uid;
    var repost_tree_link = 'http://219.224.135.60:8080/show_graph/' + mid;
    html += '<li class="item"><div class="weibo_face"><a target="_blank" href="' + user_link + '">';
    html += '<img src="' + profile_image_url + '">';
    html += '</a></div>';
    html += '<div class="weibo_detail">';
    html += '<p>排名:'+rank+'&nbsp;&nbsp;昵称:<a class="undlin" target="_blank" href="' + user_link  + '">' + uname + '</a>&nbsp;&nbsp;(' + location + ')&nbsp;&nbsp;领域:' + domain + '&nbsp;&nbsp;发布ip:' + geo + '&nbsp;&nbsp;发布内容:&nbsp;&nbsp;' + text + '</p>';
    html += '<div class="weibo_info">';
    html += '<div class="weibo_pz">';
    html += '<a class="undlin" href="javascript:;" target="_blank">转发数(' + reposts_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
    html += '<a class="undlin" href="javascript:;" target="_blank">粉丝数(' + friends_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
    html += '<a class="undlin" href="javascript:;" target="_blank">关注数(' + followers_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
    html += '<a class="undlin" href="javascript:;" target="_blank">微博数(' + statuses_count + ')</a></div>';
    html += '<div class="m">';
    html += '<a class="undlin" target="_blank" href="' + weibo_link + '">' + timestamp + '</a>&nbsp;-&nbsp;';
    html += '<a target="_blank" href="' + weibo_link + '">微博</a>&nbsp;-&nbsp;';
    html += '<a target="_blank" href="' + user_link + '">用户</a>&nbsp;-&nbsp;';
    html += '<a target="_blank" href="#">画像</a>&nbsp;-&nbsp;';
    html += '<a target="_blank" href="' + repost_tree_link + '">转发树</a>';
    html += '</div>'
    html += '</div>'
    html += '</div>'
    html += '</li>'
   } 
   $("#trend_maker_ul").append(html);
   $("#maker_content_control_height").css("height", $("#weibo_ul").css("height"));
   trendmaker_more(data,start_row,end_row);
}

function tr_pusher_request_callback(data,start_row,end_row){
    $("#trend_pusher_ul").empty();
  if (data.length){
   $("#loading_current_data5").text("计算完成!");
  }
  
  var html = "";
  //注意这里的翻页还要做处理
    N=data.length;
   
   for(var i = start_row; i < end_row; i += 1){
    var firstuser_item = data[i]
    var rank = firstuser_item[0]
    var uid = firstuser_item[1]
    var uname = firstuser_item[2]
    var location = firstuser_item[3]
    var domain = firstuser_item[4]
    var timestamp = firstuser_item[5]
    var text = firstuser_item[6]
    var profile_image_url = firstuser_item[7]
    if (profile_image_url == 'no'){
      profile_image_url = '/static/img/unknown_profile_image.gif';
    }
    var friends_count = firstuser_item[8]
    var followers_count = firstuser_item[9]
    var statuses_count = firstuser_item[10]
    var created_at = firstuser_item[11]
    var geo = firstuser_item[12]
    if (geo==null){
      geo = '未知';
    }
    var source = firstuser_item[13]
    var weibo_link = firstuser_item[14]
    var mid = firstuser_item[15]
    var reposts_count = firstuser_item[16]
    var user_link = 'http://weibo.com/u/' + uid;
    var repost_tree_link = 'http://219.224.135.60:8080/show_graph/' + mid;
    html += '<li class="item"><div class="weibo_face"><a target="_blank" href="' + user_link + '">';
    html += '<img src="' + profile_image_url + '">';
    html += '</a></div>';
    html += '<div class="weibo_detail">';
    html += '<p>排名:'+rank+'&nbsp;&nbsp;昵称:<a class="undlin" target="_blank" href="' + user_link  + '">' + uname + '</a>&nbsp;&nbsp;(' + location + ')&nbsp;&nbsp;领域:' + domain + '&nbsp;&nbsp;发布ip:' + geo + '&nbsp;&nbsp;发布内容:&nbsp;&nbsp;' + text + '</p>';
    html += '<div class="weibo_info">';
    html += '<div class="weibo_pz">';
    html += '<a class="undlin" href="javascript:;" target="_blank">转发数(' + reposts_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
    html += '<a class="undlin" href="javascript:;" target="_blank">粉丝数(' + friends_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
    html += '<a class="undlin" href="javascript:;" target="_blank">关注数(' + followers_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
    html += '<a class="undlin" href="javascript:;" target="_blank">微博数(' + statuses_count + ')</a></div>';
    html += '<div class="m">';
    html += '<a class="undlin" target="_blank" href="' + weibo_link + '">' + timestamp + '</a>&nbsp;-&nbsp;';
    html += '<a target="_blank" href="' + weibo_link + '">微博</a>&nbsp;-&nbsp;';
    html += '<a target="_blank" href="' + user_link + '">用户</a>&nbsp;-&nbsp;';
    html += '<a target="_blank" href="#">画像</a>&nbsp;-&nbsp;';
    html += '<a target="_blank" href="' + repost_tree_link + '">转发树</a>';
    html += '</div>'
    html += '</div>'
    html += '</div>'
    html += '</li>'
   } 
   $("#trend_pusher_ul").append(html);
   $("#pusher_content_control_height").css("height", $("#weibo_ul").css("height"));
   trendpusher_more(data,start_row,end_row);

}

function request_callback2(data) {
        rankdata = data;
        var status = 'current finished';
        var page_num = 10 ;
        if (status == 'current finished') {
            $("#current_process_bar").css('width', "100%")
            $("#current_process").removeClass("active");
            $("#current_process").removeClass("progress-striped");
            current_data = rankdata;

            if (current_data.length) {
               
                $("#loading_current_data2").text("计算完成!");
                if (current_data.length < page_num) {
                    $('#rank_page_selection2').empty();
                    page_num = current_data.length
                    create_current_table2(current_data, 0, page_num, 'pro');
                }
                else {
                    create_current_table2(current_data, 0, page_num, 'pro');
                    var total_pages = 0;
                    if (current_data.length % page_num == 0) {
                        total_pages = current_data.length / page_num;
                    }
                    else {
                        total_pages = current_data.length / page_num + 1;
                    }
            
                    $('#rank_page_selection2').bootpag({
                        total: total_pages,
                        page: 1,
                        maxVisible: 30
                    }).on("page", function(event, num){
                        start_row = (num - 1)* page_num;
                        end_row = start_row + page_num;
                        if (end_row > current_data.length)
                            end_row = current_data.length;
                            create_current_table2(current_data, start_row, end_row, 'pro');
                    });
                }
            }
            else {
                $("#rank_table2").empty();
                $("#loading_current_data2").text("很抱歉，本期计算结果为空!");
            }
        }
        else{
            return
        }
    }

function filter_node_in_network2(node_uid){
    show_network2();
    filter
      .undo('filter_node2')
      .nodesBy(function(n) {
        return n.label == String(node_uid);
      }, 'filter_node2')
      .apply();
}

//首发用户的表格显示
function create_firstuser_table(data, start_row, end_row, type){
  //此处的type没有作用了
  $("#firstuser_table").empty(); //firstuser_table要在html中写出来
  
  var cellCount = 7;
  var table = '<table class="table table-bordered">';
  var thead = '<thead><tr><th>排名</th><th style="display:none">博主ID</th><th>博主昵称</th><th>博主地域</th><th>博主领域</th><th>微博发布时间</th><th>微博内容</th></thead>'
  var tbody = '<tbody>';
  for (var i = start_row; i <end_row; i++){
    var tr = '<tr>';
    for (var j = 0;j < cellCount; j++){
      if (j == 0) {
        var td = '<td><span class="label label-important">'+data[i][j]+'</span></td>';
      }
      else if(j == 1){
            var td = '<td style="display:none">'+data[i][j]+'</td>';
      }
      else if(j == 2){
            var td = '<td>'+data[i][j]+'</td>';
        }
      else if(j == 3){
            var td = '<td>'+data[i][j]+'</td>';
        }
      else if(j == 4){
            var td = '<td>'+data[i][j]+'</td>';
        }
      else if(j == 5){
            var td = '<td>'+data[i][j]+'</td>';
        }
      else if(j == 6){
            var td = '<td>'+data[i][j]+'</td>';
        }
      tr += td
    }
    tr += '</tr>';
    tbody += tr;
  }
  tbody += '</tbody>';
  table += thead + tbody;
  table += '</table>';


  $("#firstuser_table").html(table);
}


//data的数据结构需要再确定
function create_current_table2(data, start_row, end_row, type) {
    $("#rank_table2").empty();
    //console.log('create_current_table2');
    //console.log(data);
    var cellCount = 10;
    var table = '<table class="table table-bordered">';
    var thead = '<thead><tr><th>排名</th><th style="display:none">博主ID</th><th>博主昵称</th><th>博主地域</th><th>粉丝数</th><th>关注数</th><th>PR值</th><th>度中心性</th><th>介数中心性</th><th>紧密中心性</th></tr></thead>';
    var tbody = '<tbody>';
    //var rank = 0;
    for (var i = start_row;i < end_row;i++) {
      var tr = '<tr>';
      var rank = i+1;
      for(var j = 0;j < cellCount;j++) {
        if(j == 0) {
          // rank status
          var td = '<td><span class="label label-important">'+rank+'</span></td>';
        }
        else if(j == 1){
            var td = '<td style="display:none">'+data[i][j]+'</td>';
        }
        else if(j == 2){
            var td = '<td><a href=\"#network2\" onclick=\"filter_node_in_network2(' + data[i][1] + ')\">' + data[i][j] + '</a></td>';
        }
        else if(j == 3){
            var td = '<td>'+data[i][j]+'</td>';
        }
        else if(j == 4){
            var td = '<td>'+data[i][j]+'</td>';
        }
        else if(j == 5){
            var td = '<td>'+data[i][j]+'</td>';
        }
        else{
            var td = '<td>'+data[i][j].toFixed(3)+'</td>';
        }
        tr += td;
      }
      tr += '</tr>';
      tbody += tr;
    }
    tbody += '</tbody>';
    table += thead + tbody;
    table += '</table>';

    $("#rank_table2").html(table);
}


var index = [];
var value = [];
var x_data = [];
var y_data = [];
var topn = 100;

function get_firstuser(rank_method){
  $.ajax({
    url: "/identify/first_user/?topic="+ topic + '&start_ts=' + start_ts + '&end_ts=' + end_ts + '&rank_method=' + rank_method,
    dataType: "json",
    type:'Get',
    async:false,
    success:function(data){
      var start_row = 0; var end_row = 5;
      fu_ul_request_callback(data,start_row,end_row);

    }
  });
}

function get_domain_firstuser_folk(rank_method){
  domain = 'folk'
  $.ajax({
    url:"/identify/domain_first_user/?topic="+ topic + '&start_ts=' + start_ts + '&end_ts=' + end_ts + '&domain=' + domain + '&rank_method=' + rank_method,
    dataType:"json",
    type:"Get",
    async:false,
    success:function(data){
      
      var start_row = 0; var end_row = 5;
      fu_ul_request_callback(data,start_row,end_row);
    }
  });
}
function get_domain_firstuser_media(rank_method){
  domain = 'media'
  $.ajax({
    url:"/identify/domain_first_user/?topic="+ topic + '&start_ts=' + start_ts + '&end_ts=' + end_ts + '&domain=' + domain + '&rank_method=' + rank_method,
    dataType:"json",
    type:"Get",
    async:false,
    success:function(data){
      var start_row = 0; var end_row = 5;
      fu_ul_request_callback(data,start_row,end_row);
    }
  });
}
function get_domain_firstuser_opinionleader(rank_method){
  domain = 'opinion_leader'
  $.ajax({
    url:"/identify/domain_first_user/?topic="+ topic + '&start_ts=' + start_ts + '&end_ts=' + end_ts + '&domain=' + domain + '&rank_method=' + rank_method,
    dataType:"json",
    type:"Get",
    async:false,
    success:function(data){
      
      var start_row = 0; var end_row = 5;
      fu_ul_request_callback(data,start_row,end_row);
    }
  });
}
function get_domain_firstuser_oversea(rank_method){
  domain = 'oversea'
  $.ajax({
    url:"/identify/domain_first_user/?topic="+ topic + '&start_ts=' + start_ts + '&end_ts=' + end_ts + '&domain=' + domain + '&rank_method=' + rank_method,
    dataType:"json",
    type:"Get",
    async:false,
    success:function(data){
      
      var start_row = 0; var end_row = 5;
      fu_ul_request_callback(data,start_row,end_row);
    }
  });
}
function get_domain_firstuser_other(rank_method){
  domain = 'other'
  $.ajax({
    url:"/identify/domain_first_user/?topic="+ topic + '&start_ts=' + start_ts + '&end_ts=' + end_ts + '&domain=' + domain + '&rank_method=' + rank_method,
    dataType:"json",
    type:"Get",
    async:false,
    success:function(data){
      
      var start_row = 0; var end_row = 5;
      fu_ul_request_callback(data,start_row,end_row);
    }
  });
}

function get_trend_maker(rank_method){
  $.ajax({
    url:"/identify/trend_maker/?topic=" + topic + "&start_ts=" + start_ts + "&end_ts=" + end_ts + '&rank_method=' + rank_method, 
    dataType:"json",
    type:"Get",
    async:false,
    success:function(data){
      var start_row = 0; var end_row = 5;
      tr_maker_request_callback(data,start_row,end_row);
    }
  });
}

function get_trend_pusher(rank_method){
  $.ajax({
    url:"/identify/trend_pusher/?topic=" + topic + "&start_ts=" + start_ts + "&end_ts=" + end_ts + '&rank_method=' + rank_method,
    dataType:"json",
    type:"Get",
    async:false,
    success:function(data){
      //console.log(data);
      var start_row = 0; var end_row = 5;
      tr_pusher_request_callback(data,start_row,end_row);
    }
  }
    );
  }

function get_pagerank2(domain){
      $.ajax({
      url: "/identify/ds_pr_rank/?topic="+ topic +'&start_ts=' + start_ts +'&end_ts=' + end_ts + '&topn=' + topn + '&network_type=' + network_type2 + '&domain=' + domain,
      dataType : "json",
      type : 'GET',
      async: false,
      success: function(data){
        //console.log('get_pagerank2');
        //console.log(data);
        request_callback2(data);
      }  
  }) ; 
}

// function get_trendsetterrank(domain){
//   $.ajax({
//     url: "/identify/ds_tr_rank/?topic=" + topic + "&start_ts=" + start_ts + "&end_ts=" + end_ts + "&topn=" + topn + '&domain=' + domain,
//     dataType:"json",
//     type:'Get',
//     async:false,
//     success:function(data){
     
//       request_callback2(data);
//     }
//   }
//     );
// }

function get_centrelity2(domain){
        $.ajax({
      url: "/identify/ds_degree_centrality_rank/?topic="+ topic +'&start_ts=' + start_ts +'&end_ts=' + end_ts + '&network_type=' + network_type2 + '&domain=' + domain,
      dataType : "json",
      type : 'GET',
      async: false,
      success: function(data){
        //console.log('get_centrelity2');
        //console.log(data);
        request_callback2(data);
      }  
  }) ; 
}

function betweeness_centrality_rank2(domain){
        $.ajax({
      url: "/identify/ds_betweeness_centrality_rank/?topic="+ topic +'&start_ts=' + start_ts +'&end_ts=' + end_ts + '&network_type=' + network_type2 + '&domain=' + domain,
      dataType : "json",
      type : 'GET',
      async: false,
      success: function(data){
        //console.log('betweeness_centrality_rank2');
        //console.log(data);
        request_callback2(data);
      }  
  }) ; 
        
}

function closeness_centrality_rank2(domain){
        $.ajax({
      url: "/identify/ds_closeness_centrality_rank/?topic="+ topic +'&start_ts=' + start_ts +'&end_ts=' + end_ts + '&network_type=' + network_type2 + '&domain=' + domain,
      dataType : "json",
      type : 'GET',
      async: false,
      success: function(data){
      //console.log('closeness_centrality_rank2');
      //console.log(data);  
      request_callback2(data);
      }  
  }) ;

}

// function get_ntr_rank(domain){
//   $.ajax({
//     url:"/identify/ntr/?topic=" + topic +'&start_ts=' + start_ts + '&end_ts=' + end_ts + '&domain=' + domain,
//     dataType:"json",
//     type:'GET',
//     async:false,
//     success:function(data){
      
//       request_callback2(data);
//     }
//   });
// }

function getnetwork_line2(){

    var indegree_x = [];
    var indegree_y = [];
    var outdegree_x = [];
    var outdegree_y = [];
    var shortest_path_x = [];
    var shortest_path_y = [];
    $.ajax({
      url: "/identify/quota/?topic="+ topic +'&start_ts=' + start_ts +'&end_ts=' + end_ts +'&quota=shortest_path_length_histogram' + '&network_type=' + network_type2,
      dataType : "json",
      type : 'GET',
      async: false,
      success: function(data){
            for (var key in data){         
            shortest_path_x.push(key);
            shortest_path_y.push(data[key]/2);
            drawpicture2(shortest_path_x,shortest_path_y);

        }
      }

  }) ;     
}

function drawpicture2(shortest_path_x,shortest_path_y) {

    $('#line2').highcharts({
      chart: {
                type: 'spline',
            },
            title: {
            text: '网络曲线图-转发链条长度分布',
        style: {
                    color: '#666',
                    fontWeight: 'bold',
                    fontSize: '13px',
                    fontFamily: 'Microsoft YaHei'
                }
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
            text: '最短路径长度',
        style: {
                    color: '#666',
                    fontWeight: 'bold',
                    fontSize: '12px',
                    fontFamily: 'Microsoft YaHei'
                }
        },
            categories:shortest_path_x
        },
        yAxis: {
            title: {
                text: '节点数量',
                style: {
                    color: '#666',
                    fontWeight: 'bold',
                    fontSize: '12px',
                    fontFamily: 'Microsoft YaHei'
                }
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
         plotOptions: {
          spline: {
              lineWidth: 2,
              states: {
                  hover: {
                      lineWidth: 3
                  }
              },
              marker: {
                  enabled: false
              },
            }
        },
        tooltip: {
            valueSuffix: ''
        },
        legend: {
            layout: 'vertical',
            align: 'center',
            verticalAlign: 'bottom',
            borderWidth: 0,
            itemStyle: {
              color: '#666',
              fontWeight: 'bold',
              fontSize: '12px',
              fontFamily: 'Microsoft YaHei'
              }
        },
        series: [{
            name: '节点数量',
            data: shortest_path_y
        }]
    });
}

$("#submit_request2").click(function(){
  var check_rank_method = $("#select21").val();
  var check_domain_method = $("#select22").val();
  
  if (check_rank_method=="pr_method"){
     get_pagerank2(check_domain_method);
  }
  else if(check_rank_method=="dc_method"){
     get_centrelity2(check_domain_method);
  }
  else if(check_rank_method=="bc_method"){
     betweeness_centrality_rank2(check_domain_method);
  }
  else{
      closeness_centrality_rank2(check_domain_method);
  }

});

$("#submit_fu_request").click(function(){
  var fu_domain = $("#select_fu_domain").val();
  var rank_method = $("#select_fu_rank_method").val();
  //console.log(fu_domain);
  if (fu_domain=="fu_all"){
    get_firstuser(rank_method);
  }
  else if(fu_domain=="folk"){
    get_domain_firstuser_folk(rank_method);
  }
  else if(fu_domain=="media"){
    get_domain_firstuser_media(rank_method);
  }
  else if(fu_domain=="opinion_leader"){
    get_domain_firstuser_opinionleader(rank_method);
  }
  else if(fu_domain=="oversea"){
    get_domain_firstuser_oversea(rank_method);
  }
  else{
    get_domain_firstuser_other(rank_method);
  }
});
$("#submit_trendmaker_request").click(function(){
  var rank_method = $("#select_trendmaker_rank").val();
  //console.log(rank_method);
  get_trend_maker(rank_method);
});
$("#submit_trendpusher_request").click(function(){
  var rank_method = $("#select_trendpusher_rank").val();
  //console.log(rank_method);
  get_trend_pusher(rank_method);
});
