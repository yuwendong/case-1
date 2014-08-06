var previous_data = null;
var current_data = null;

function show_user_statuses(uid,time_ts) {
	window.location.href='/identify/statuses/'+uid+'/1/'+time_ts;
}

(function ($) {
    function request_callback(data) {
	var status = data['status'];
	var current_data = data['data'];
	var pre_data = data['pre_data'];
	var method = data['method'];
	var time_ts = data['time'];
	if (status == 'current finished') {
		    $("#current_process_bar").css('width', "100%")
		    $("#current_process").removeClass("active");
		    $("#current_process").removeClass("progress-striped");
		    current_data = current_data;
		    $("#previous_process_bar").css('width', "100%")
		    $("#previous_process").removeClass("active");
		    $("#previous_process").removeClass("progress-striped");
		    previous_data = pre_data;
		    if (current_data.length) {
				$("#loading_current_data").text("计算完成!");
				if (current_data.length < page_num) {
				    page_num = current_data.length;
				    if (method == 'active'){
				    create_current_table1(current_data, 0, page_num, time_ts);
				  	}
				  	else{
				  		create_current_table2(current_data, 0, page_num, time_ts);
				  	}
				}
				else {
				    if (method == 'active'){
				    create_current_table1(current_data, 0, page_num, time_ts);
				  	}
				  	else{
				  		create_current_table2(current_data, 0, page_num, time_ts);
				  	}
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
					if (method == 'active'){
					create_current_table1(current_data, start_row, end_row, time_ts);
					}
					else{
						create_current_table2(current_data, start_row, end_row, time_ts);
					}
				    });
				}
		    }
		    else{
				$("#loading_current_data").text("很抱歉，本期计算结果为空!");
		    }
		    if (previous_data.length) {
				$("#loading_previous_data").text("计算完成!");
				if (previous_data.length < page_num) {
				    page_num = previous_data.length
				    if (method == 'active'){
				    create_previous_table1(previous_data, 0, page_num, time_ts);
				  }
				  else{
				  	create_previous_table2(previous_data, 0, page_num, time_ts);
				  }
				}
				else {
				    if (method == 'active'){
				    create_previous_table1(previous_data, 0, page_num, time_ts);
				  }
				  else{
				  	create_previous_table2(previous_data, 0, page_num, time_ts);
				  }
				    var total_pages = 0;
				    if (previous_data.length % page_num == 0) {
					total_pages = previous_data.length / page_num;
				    }
				    else {
					total_pages = previous_data.length / page_num + 1;
				    }
				    $('#previous_rank_page_selection').bootpag({
					total: total_pages,
					page: 1,
					maxVisible: 30
				    }).on("page", function(event, num){
					start_row = (num - 1)* page_num;
					end_row = start_row + 20;
					if (end_row > previous_data.length)
					    end_row = previous_data.length;
					if (method == 'active'){
					create_previous_table1(previous_data, start_row, end_row, time_ts);
					}
					else{
						create_previous_table2(previous_data, start_row, end_row, time_ts);
					}
				    });
				}
		    }
		    else {
				$("#loading_previous_data").text("很抱歉，上期结果不存在!");
		    }		    
		}
		else
		    return
    }
    
    function create_current_table1(data, start_row, end_row, time_ts) {
	var cellCount = 12;
	var table = '<table class="table table-bordered">';
	var thead = '<thead><tr><th>排名</th><th  style="display:none">博主ID</th><th>博主昵称</th><th>博主地域</th><th>关注数</th><th>粉丝数</th><th>活跃度</th><th>重要度</th><th>活跃度差值</th><th>敏感状态</th><th>环比</th><th>全选<input id="select_all" type="checkbox" /></th></tr></thead>';
	var tbody = '<tbody>';
	
	for (var i = start_row;i < end_row;i++) {
        var tr = '<tr>';

	    if (data[i][3].match("海外")) {
			tr = '<tr class="success">';
	    }
	    var uid = data[i][1];
            for(var j = 0;j < cellCount;j++) {
		if (j == 11) {
		    // checkbox
		    var td = '<td><input id="uid_'+ data[i][1] + '" type="checkbox" name="now_user"></td>';
		}
		else if (j == 9) {
		    // identify status
		    if (data[i][j])
			var td = '<td><i class="icon-ok"></i></td>';
		    else
			var td = '<td><i class="icon-remove"></i></td>';
		}
		else if(j == 10) {
		    // comparsion
		    if (data[i][j] > 0)
			var td = '<td><i class="icon-arrow-up"></i>'+ data[i][j] + '</td>';
		    else if (data[i][j] < 0)
			var td = '<td><i class="icon-arrow-down"></i>'+ data[i][j] + '</td>';
		    else
			var td = '<td><i class="icon-minus"></i></td>';
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
    function create_current_table2(data, start_row, end_row, time_ts) {
	var cellCount = 12;
	var table = '<table class="table table-bordered">';
	var thead = '<thead><tr><th>排名</th><th  style="display:none">博主ID</th><th>博主昵称</th><th>博主地域</th><th>关注数</th><th>粉丝数</th><th>活跃度</th><th>重要度</th><th>重要度差值</th><th>敏感状态</th><th>环比</th><th>全选<input id="select_all" type="checkbox" /></th></tr></thead>';
	var tbody = '<tbody>';
	for (var i = start_row;i < end_row;i++) {
        var tr = '<tr>';
 
	    if (data[i][3].match("海外")) {
			tr = '<tr class="success">';
	    }
	    var uid = data[i][1];
            for(var j = 0;j < cellCount;j++) {
		if (j == 11) {
		    // checkbox
		    var td = '<td><input id="uid_'+ data[i][1] + '" type="checkbox" name="now_user"></td>';
		}
		else if (j == 9) {
		    // identify status
		    if (data[i][j])
			var td = '<td><i class="icon-ok"></i></td>';
		    else
			var td = '<td><i class="icon-remove"></i></td>';
		}
		else if(j == 10) {
		    // comparsion
		    if (data[i][j] > 0)
			var td = '<td><i class="icon-arrow-up"></i>'+ data[i][j] + '</td>';
		    else if (data[i][j] < 0)
			var td = '<td><i class="icon-arrow-down"></i>'+ data[i][j] + '</td>';
		    else
			var td = '<td><i class="icon-minus"></i></td>';
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

    function create_previous_table1(data, start_row, end_row, time_ts) {
	var cellCount = 10;
	var table = '<table class="table table-bordered">';
	var thead = '<thead><tr><th>排名</th><th  style="display:none">博主ID</th><th>博主昵称</th><th>博主地域</th><th>关注数</th><th>粉丝数</th><th>活跃度</th><th>重要度</th><th>活跃度差值</th><th>敏感状态</th></tr></thead>';
	var tbody = '<tbody>';
	for (var i = start_row;i < end_row;i++) {
            var tr = '<tr>';
	    var uid = data[i][1];
	    if (data[i][3].match("海外")) {
		tr = '<tr class="success">';
	    }
            for(var j = 0;j < cellCount;j++) {
		if (j == 9) {
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
	$("#previous_rank_table").html(table);
    }
    
    function create_previous_table2(data, start_row, end_row, time_ts) {
	var cellCount = 10;
	var table = '<table class="table table-bordered">';
	var thead = '<thead><tr><th>排名</th><th  style="display:none">博主ID</th><th>博主昵称</th><th>博主地域</th><th>关注数</th><th>粉丝数</th><th>活跃度</th><th>重要度</th><th>重要度差值</th><th>敏感状态</th></tr></thead>';
	var tbody = '<tbody>';
	for (var i = start_row;i < end_row;i++) {
            var tr = '<tr>';
	    var uid = data[i][1];
	    if (data[i][3].match("海外")) {
		tr = '<tr class="success">';
	    }
            for(var j = 0;j < cellCount;j++) {
		if (j == 9) {
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
	$("#previous_rank_table").html(table);
    }

    function identify_request() {
	// previous results
	$.post("/identify/burst/", {'action': 'rank', 'rank_method': rank_method, 'burst_time': burst_time, 'top_n': top_n}, request_callback, "json");
    }

    identify_request();

})(jQuery);