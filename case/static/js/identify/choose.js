function choose_method(range, method) {
    $("#"+range+"_rank_method").val(method);
    cn_method = '';
    if(method=='followers')
        cn_method = '粉丝数';
    else if(method=='active')
	cn_method = '活跃度';
    else if(method=='important')
	cn_method = '重要度';
    $("#"+range+"_rank_method_choosen").text(cn_method);
    $("#"+range+"_rank_method_choosen").append(' <span class="caret"></span>');
    //close dropdown
    $("#"+range+"_rank_method_choosen").parent().removeClass('open');
    $("#"+range+"_rank_method_dropdown_menu").children().removeClass('active');
}

function choose_method2(range, method) {
    $("#"+range+"_rank_method").val(method);
    cn_method = '';
		if(method=='active')
	cn_method = '活跃度差值';
    else if(method=='important')
	cn_method = '重要度差值';
    $("#"+range+"_rank_method_choosen").text(cn_method);
    $("#"+range+"_rank_method_choosen").append(' <span class="caret"></span>');
    //close dropdown
    $("#"+range+"_rank_method_choosen").parent().removeClass('open');
    $("#"+range+"_rank_method_dropdown_menu").children().removeClass('active');
}

function choose_window(range, window) {
    $("#"+range+"_window_size").val(window);
    cn_window = '';
    if(window==1)
        cn_window = '1天';
    else if(window==7)
	cn_window = '1周';
    else if(window==30)
	cn_window = '1个月';
    else if(window==90)
	cn_window = '3个月';
    $("#"+range+"_window_size_choosen").text(cn_window);
    $("#"+range+"_window_size_choosen").append(' <span class="caret"></span>');
    //close dropdown
    $("#"+range+"_window_size_choosen").parent().removeClass('open');
    $("#"+range+"_window_size_dropdown_menu").children().removeClass('active');
}