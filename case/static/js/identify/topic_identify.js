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
var  name = ['number_edges', 'number_nodes','ave_degree_centrality', 'ave_degree_centrality',
 'ave_closeness_centrality','eigenvector_centrality','number_strongly_connected_components',
 'average_shortest_path_length','ave_eccentricity','power_law_distribution','ave_degree',
 'diameter','power_law_distribution','number_weakly_connected_components',
 'degree_assortativity_coefficient','average_clustering','ave_k_core','ratio_H2G'];
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
  html += "<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">k核数<i id=\"trend_tooltip\" class=\"glyphicon glyphicon-question-sign\" data-toggle=\"tooltip\" data-placement=\"right\" title=\"若一个节点存在于k-核，而在（k-1）-核中被移去，那么此节点的核数为k\"></i>&nbsp;&nbsp;<span class=\"tsp\">   : </span>"+quota['ave_k_core'].toExponential(2)+"</div><div class=\"lrRr\"></div></div></th></tr>";
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
  html2 +="<th><div class=\"lrRadius\"><div class=\"lrRl\"></div><div class=\"lrRc\">最大连通子图的节点数占总图比<span class=\"tsp\">   : </span>"+quota['ratio_H2G'].toExponential(2)+"</div><div class=\"lrRr\"></div></div></th></tr>";
  $("#mstable2").append(html2);
}


$(document).ready(function(){
    get_network_infor();
    getnetwork_frequency();
    drawpicture(index,value);
    // switch_curr_add();
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


function updatePane (graph, filter) {
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
  _.$('min-degree').max = maxDegree;
  _.$('max-degree-value').textContent = maxDegree;

  _.$('min-pagerank').max = maxPagerank * 100000000;
  _.$('max-pagerank-value').textContent = maxPagerank * 100000000;
  
  // node category
  var nodecategoryElt = _.$('node-category');
  // Object.keys(categories).forEach(function(c) {
  categoriesSortedTop10.forEach(function(c) {
    var optionElt = document.createElement("option");
    optionElt.text = c;
    nodecategoryElt.add(optionElt);
  });

  // reset button
  _.$('reset-btn').addEventListener("click", function(e) {
    _.$('min-degree').value = 0;
    _.$('min-degree-val').textContent = '0';
    _.$('min-pagerank').value = 0;
    _.$('min-pagerank-val').textContent = '0';
    _.$('node-category').selectedIndex = 0;
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
    $('#linLogModeInput').val($(this).val());
});
$("input[name='outboundAttractionRadios']").on("click", function(){
    $('#outboundAttractionInput').val($(this).val());
});
$("input[name='adjustSizesRadios']").on("click", function(){
    $('#adjustSizesInput').val($(this).val());
});
$("input[name='strongGravityModeRadios']").on("click", function(){
    $('#strongGravityModeInput').val($(this).val());
});

function change_edgeWeightInfluence(){
    $('#edgeWeightInfluence_span').html($('#edgeWeightInfluence_input').val());
}

function change_scalingRatio(){
    $('#scalingRatio_span').html($('#scalingRatio_input').val());
}

function change_gravity(){
    $('#gravity_span').html($('#gravity_input').val());
}

function change_slowdown(){
    $('#slowdown_span').html($('#slowdown_input').val());
}

function network_request_callback(data) {
    $("#network_progress").removeClass("active");
    $("#network_progress").removeClass("progress-striped");
    networkUpdated = 1;

    if (data) {
        $("#loading_network_data").text("计算完成!");
        $("#sigma-graph").show();

        sigma.parsers.gexf(data, {
            container: 'sigma-graph',
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

              updatePane(s.graph, filter);

              function applyMinDegreeFilter(e) {
                var v = e.target.value;
                _.$('min-degree-val').textContent = v;

                filter
                  .undo('min-degree')
                  .nodesBy(function(n) {
                    return this.degree(n.id) >= v;
                  }, 'min-degree')
                  .apply();
              }

              function applyCategoryFilter(e) {
                var c = e.target[e.target.selectedIndex].value;
                filter
                  .undo('node-category')
                  .nodesBy(function(n) {
                    return !c.length || n.attributes.acategory === c;
                  }, 'node-category')
                  .apply();
              }

              function applyMinPagerankFilter(e) {
                var v = e.target.value;
                _.$('min-pagerank-val').textContent = v;

                filter
                  .undo('min-pagerank')
                  .nodesBy(function(n) {
                    return n.attributes.pagerank * 100000000 >= v;
                  }, 'min-pagerank')
                  .apply();
              }

              function applyZhibiaoCategoryFilter(e){
                var v = e.target.value;
                _.$('min-degree').value = 0;
                _.$('min-degree-val').textContent = '0';
                _.$('min-pagerank').value = 0;
                _.$('min-pagerank-val').textContent = '0';
                _.$('node-category').selectedIndex = 0;
                filter.undo().apply();
                if(v == 'degree'){
                    $('#min_degree_container').removeClass('hidden');
                    $('#min_pagerank_container').addClass('hidden');
                }
                if(v == 'pagerank'){
                    $('#min_pagerank_container').removeClass('hidden');
                    $('#min_degree_container').addClass('hidden');
                }
              }

              _.$('min-degree').addEventListener("input", applyMinDegreeFilter);  // for Chrome and FF
              _.$('min-degree').addEventListener("change", applyMinDegreeFilter); // for IE10+, that sucks
              _.$('min-pagerank').addEventListener("input", applyMinPagerankFilter);  // for Chrome and FF
              _.$('min-pagerank').addEventListener("change", applyMinPagerankFilter); // for IE10+, that sucks
              _.$('zhibiao-category').addEventListener("change", applyZhibiaoCategoryFilter);
              _.$('node-category').addEventListener("change", applyCategoryFilter);

              // Start the ForceAtlas2 algorithm:
              var linLogMode = ($('#linLogModeInput').val() === 'true');
              var outboundAttractionDistribution = ($('#outboundAttractionInput').val() === 'true');
              var adjustSizes = ($('#adjustSizesInput').val() === 'true');
              var strongGravityMode = ($('#strongGravityInput').val() === 'true');
              var edgeWeightInfluence = parseInt($('#edgeWeightInfluence_input').val());
              var scalingRatio = parseInt($('#scalingRatio_input').val());
              var gravity = parseInt($('#gravity_input').val());
              var slowDown = parseInt($('#slowdown_input').val());
              var config = {
                  linLogMode: linLogMode,
                  outboundAttractionDistribution: outboundAttractionDistribution,
                  adjustSizes: adjustSizes,
                  edgeWeightInfluence: edgeWeightInfluence,
                  scalingRatio: scalingRatio,
                  strongGravityMode: strongGravityMode,
                  gravity: gravity,
                  slowDown: slowDown
              }
              s.startForceAtlas2(config);

              $("#refresh_layout").click(function(){
                  //s.stopForceAtlas2();
                  var linLogMode = ($('#linLogModeInput').val() === 'true');
                  var outboundAttractionDistribution = ($('#outboundAttractionInput').val() === 'true');
                  var adjustSizes = ($('#adjustSizesInput').val() === 'true');
                  var strongGravityMode = ($('#strongGravityInput').val() === 'true');
                  var edgeWeightInfluence = parseInt($('#edgeWeightInfluence_input').val());
                  var scalingRatio = parseInt($('#scalingRatio_input').val());
                  var gravity = parseInt($('#gravity_input').val());
                  var slowDown = parseInt($('#slowdown_input').val());
                  var config = {
                      linLogMode: linLogMode,
                      outboundAttractionDistribution: outboundAttractionDistribution,
                      adjustSizes: adjustSizes,
                      edgeWeightInfluence: edgeWeightInfluence,
                      scalingRatio: scalingRatio,
                      strongGravityMode: strongGravityMode,
                      gravity: gravity,
                      slowDown: slowDown
                  }
                  s.configForceAtlas2(config);
                  s.startForceAtlas2();
              });

              $("#pause_layout").click(function(){
                  s.stopForceAtlas2();
              });

              $("#pause_layout").click(function(){
                  s.killForceAtlas2();
              });

                // We first need to save the original colors of our
                // nodes and edges, like this:
                s.graph.nodes().forEach(function(n) {
                  n.originalColor = n.color;
                });
                s.graph.edges().forEach(function(e) {
                  e.originalColor = e.color;
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

                  $('#nickname').html(node_name);
                  $('#location').html(node_location);
                  $('#user_link').html('<a target="_blank" href="http://weibo.com/u/' + node_uid + '">http://weibo.com/u/' + node_uid + '</a>');
                  $('#pagerank').html(node_pagerank);
                  $('#community').html(node_community);

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
        $("#loading_network_data").text("暂无结果!");
    }

}

function show_network() {
    networkShowed = 0;
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
                    networkdata = data;
                    network_request_callback(data);
                },
                error: function(result) {
                    $("#loading_network_data").text("暂无结果!");
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




var topic = "中国";
var start_ts = 1377965700;
var end_ts = 1378051200;
var index = [];
var value = [];
var x_data = [];
var y_data = [];


function getnetwork_frequency(){

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
        }
    }) ;
            $.ajax({
      url: "/identify/quota/?topic="+ topic +'&start_ts=' + start_ts +'&end_ts=' + end_ts +'&quota=xydict_lnx' ,
      dataType : "json",
      type : 'GET',
      async: false,
      success: function(data){
        
      for (var i = 0; i< data.length; i ++){
          var xdata = Number(data[i].toFixed(3));
          x_data.push(xdata);
        }
        // console.log(x_data);
      }
  }) ; 
            $.ajax({
      url: "/identify/quota/?topic="+ topic +'&start_ts=' + start_ts +'&end_ts=' + end_ts +'&quota=xydict_lny' ,
      dataType : "json",
      type : 'GET',
      async: false,
      success: function(data){
     
      for (var i = 0; i< data.length; i ++){
          var ydata = Number(data[i].toFixed(3));
          y_data.push(ydata);
        } 
      }  
  }) ; 


            $.ajax({
      url: "/identify/quota/?topic="+ topic +'&start_ts=' + start_ts +'&end_ts=' + end_ts +'&quota=H_degree_histogram' ,
      dataType : "json",
      type : 'GET',
      async: false,
      success: function(data){
        // console.log(data);
        H_degree_histogram = data;
      }  
  }) ;

  // drawpicture_H(index,H_degree_histogram);
  // drawpicture_ln(x_data,y_data);
  // drawpicture(index,value);


              $.ajax({
      url: "/identify/quota/?topic="+ topic +'&start_ts=' + start_ts +'&end_ts=' + end_ts +'&quota=result_linalg' ,
      dataType : "json",
      type : 'GET',
      async: false,
      success: function(data){
        // console.log(data);
        var result_r = Number(data[0].toFixed(3));
        var result_c = Number(data[1].toFixed(3));
        // console.log(result_r);
        // console.log(result_c); 
      }
  }) ; 
         
}



function drawpicture() {
    $('#line').highcharts({
        title: {
            text: '拟合曲线公式r.lnx + C =lny [r,C] = [-2.833,-12.319]',
            align:'right',
            x : -70,
        style:{
        fontSize: '13px',
        
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
            text: '度数'
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
            align: 'center',
            verticalAlign: 'bottom',
            borderWidth: 0
        },
        series: [{
            name: '原始曲线',
            data: value
        }]

    });
}
function drawpicture_ln() {
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
            text: 'lnx'
        },
            categories:x_data,
          labels: {
                step: 20
            }
          },
        yAxis: {
            title: {
                text: 'lny'
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
            align: 'center',
            verticalAlign: 'bottom',
            borderWidth: 0
        },
        series: [{
            name: '双对数曲线',
            data: y_data
        }]

    });
}

 


function drawpicture_H(index,H_degree_histogram) {
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
            text: '度数'
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
            align: 'center',
            verticalAlign: 'bottom',
            borderWidth: 0
        },
        series: [{
            name: '最大连通子图节点度分布',
            data: H_degree_histogram
        }]

    });
}

    // function switch_curr_add(){
    //     $("[name='abs_rel_switch']").bootstrapSwitch('readonly', false);
    //     $("[name='abs_rel_switch']").on('switchChange.bootstrapSwitch', function(event, state) {

    //         if (state == true){
    //          drawpicture(index,value);
    //         }
    //             else if{
    //          drawpicture_ln(x_data,y_data);
    //         }
    //             else{
    //          drawpicture_H(index,H_degree_histogram);    

    //             }
            
    //     });

    // }
