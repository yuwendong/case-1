var showed = 0;
var top_n = 10;
var updated = 0;
function show_burst_user() {
    if (!showed) {
	$("#realtime_burst_user").removeClass('out');
	$("#realtime_burst_user").addClass('in');
	if (!updated) {
	    $.post("/identify/monitor/burst/", {'top_n': top_n}, request_callback, "json");
	}
	showed = 1;
    }
    else {
	$("#realtime_burst_user").removeClass('in');
	$("#realtime_burst_user").addClass('out');
	showed = 0;
    }
}

function request_callback(data) {
    $("#burst_user_progress").removeClass("active");
    $("#burst_user_progress").removeClass("progress-striped");
    if (data.length) {
	updated = 1;
	if(data.length < top_n)
	    top_n = data.length;
	create_table(data, 5);
    }
    else {
	$("#loading_burst_data").text("暂无结果!");
    }
}

function create_table(data, rowCount) {
    var cellCount = 10;
    var table = '<table class="table table-bordered">';
    var thead = '<thead><tr><th>排名</th><th style="display:none">博主ID</th><th>博主昵称</th><th>博主地域</th><th>关注数</th><th>粉丝数</th><th>活跃度</th><th>重要度</th><th>活跃度差值</th><th>敏感状态</th></tr></thead>';
    var tbody = '<tbody>';
    for(var i = 0;i < rowCount;i++) {
        var tr = '<tr>';
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
    $("#burst_user_table").html(table);
}