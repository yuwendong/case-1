var previous_data = null;
var current_data = null;
var networkShowed = 0;
var networkUpdated = 0;
var animation = 0;
var start_ts = null;
var end_ts = null;
var sigInst = null;
var animation_timer = null;

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
                sigInst = sigma.init($('#sigma-graph')[0]).drawingProperties({
                    defaultLabelColor: '#fff'
                }).graphProperties({
                    minNodeSize: 0.5,
                    maxNodeSize: 5
                });

                sigInst.parseGexf(data);

                sigInst.startForceAtlas2();
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
                                    if (o.attr == 'name')
                                        return '<li>' + '博主昵称' + ' : ' + o.val + '</li>';
                                    else if (o.attr == 'location')
                                        return '<li>' + '博主地域' + ' : ' + o.val + '</li>';
                                    else if (o.attr == 'timestamp')
                                        return '<li>' + '博主最早出现时间' + ' : ' + new Date(o.val*1000).format("yyyy-MM-dd") + '</li>';
                                    else
                                        return '<li>' + o.attr + ' : ' + o.val + '</li>';
                                 }).join('') + '</ul>';
                        }
                    
                    function showNodeInfo(event) {
                                popUp && popUp.remove();
                                
                                var node;
                                sigInst.iterNodes(function(n){
                                    node = n;
                                },[event.content[0]]);
                                popUp = $(
                                    '<div class="node-info-popup"></div>'
                                ).append(
                                    // The GEXF parser stores all the attributes in an array named
                                    // 'attributes'. And since sigma.js does not recognize the key
                                    // 'attributes' (unlike the keys 'label', 'color', 'size' etc),
                                    // it stores it in the node 'attr' object :
                                    attributesToString( node['attr']['attributes'] )
                                ).attr(
                                    'id',
                                    'node-info'+sigInst.getID()
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
                                
                                $('ul',popUp).css('margin','0 0 0 20px');
                                
                                $('#sigma-graph').append(popUp);
                        }
                                
                        function hideNodeInfo(event) {
                                popUp && popUp.remove();
                                popUp = false;
                        }
                                
                        sigInst.bind('overnodes',showNodeInfo).bind('outnodes',hideNodeInfo).draw();
                })();
    }

    else {
            console.log('1');
                $("#loading_network_data").text("暂无结果!");
        }

}

function show_network() {
    networkShowed = 0;
  if (!networkShowed) {
            $("#network").removeClass('out');
            $("#network").addClass('in');
            networkShowed = 0;
            if (!networkUpdated){
          $.ajax({
                    url: "/index/topic/network/",
                    
                    dataType: 'xml',
                    type: "POST",
                    success: function (data) {
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
            var status = data['status'];
            var data = data['data'];
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
            end_row = start_row + 20;
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
            var cellCount = 8;
            var table = '<table class="table table-bordered">';
            var thead = '<thead><tr><th>排名</th><th style="display:none">博主ID</th><th>博主昵称</th><th>博主地域</th><th>粉丝数</th><th>关注数</th><th>敏感状态</th><th><input id="select_all" type="checkbox" />全选</th></tr></thead>';
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
            $.post("/index/topic/", {'topic': topic, 'rank_method': rank_method, 'start_ts': begin_ts, 'end_ts': over_ts, 'page_num': page_num, 'top_n': top_n}, request_callback, "json");
    }

    identify_request();

})(jQuery);
