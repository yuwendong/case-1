/* common javascript */

function confirm_del() {
	return confirm('您确认删除吗？');
}

/*判断浏览器类型*/
var Browser_Name=navigator.appName;
var is_IE=(Browser_Name == "Microsoft Internet Explorer");//判读是否为ie浏览器
var is_NN=(Browser_Name == "Netscape");//判断是否为netscape浏览器
var is_op=(Browser_Name == "Opera");//判断是否为Opera浏览器

//thickbox on click
function tb_click(th) {
	var t = th.title || th.name || null;
	var a = th.href || th.alt;
	var g = th.rel || false;
	tb_show(t,a,g);
	this.blur();
	return false;
}

//loading
function loading() {
	var object = $('#f_loading');
	var width = $('body').width();
	var left = (width/2) - 85;
	$(object).css('left', left);
	$(object).show();
	return false;
}

function loading_position() {
	var object = $('#f_loading');
	var offsetTop = 160 + $(window).scrollTop() + 'px';
	$(object).animate({top : offsetTop },{ duration:500 , queue:false });
}

function unloading() {
	$('#f_loading').hide();
}

$(function() {
	//土豆优酷项目的百度指数的页面不要调用加载
	var isTdyk = window.location.href.match(/bd_index/);
	autoTheme();
	$('#head_nav a').click(function(){
		loading();
	});
	$('#topnav a').not($('.no_loading')).click(function(){
		loading();
	});
	$('.leftbox a').click(function(){
		if($(this).attr('id') != 'noloading') {
			loading();
		}
	});
	$('.step1 a').click(function(){
		if(!isTdyk)
		{
			loading();
		}
	});
	$('.step1_son a').click(function(){
		if(!isTdyk)
		{
			loading();
		}
	});
	$('.gson a').click(function(){
		loading();
	});
	$('.step2 a').click(function(){
		loading();
	});
	$('.step3 a').click(function(){
		loading();
	});
})

//加载报表信息列表等
function load_report(objid, url, getdata) {
	var object = $('#'+objid);
	object.html('<div class="loading"> <img align="absmiddle" src="'+base_url()+'static/images/loader.gif" border="0" /> 正在加载... </div>');
	object.load(url, getdata);
}

//加载flash图片
function load_flash(objid, url, width, height, post_data) {
	$('#P_'+objid).html('<div id="'+objid+'"><div class="loading"> <img align="absmiddle" src="'+base_url()+'static/images/loader.gif" border="0" /> 正在加载... </div></div>');
	var object = $('#'+objid);
	
	$.post(url, post_data, function(data){
		if (data == 'err') {
			object.html('此统计数据暂未生成。');
		}else if(data == ''){
			object.html('此统计数据暂未生成。');
		}else {
			object.html('');
			swfobject.embedSWF(base_url()+"static/swf/open-flash-chart.swf", objid, width, height, "9.0.0", "expressInstall.swf",
				{"data-file":data+"?code="+Math.random(),"loading":"数据加载中,请稍后..."},{'wmode':'transparent'}
			);
			if(!is_IE){
				object.append( '<param name="movie" value="" />' ); 
				object.append( '<param name="wmode" value="transparent" />' );
			}
		}
	});
}

/* tab */
function setTab(name,cursel,n) {
	for(i=1; i<=n; i++) {
		var menu = document.getElementById(name+i);
		var con = document.getElementById("con_"+name+"_"+i);
		menu.className = i==cursel ? "hover" : "";
		con.style.display = i==cursel ? "block" : "none";
	}
}

/* show export */
function show_export(objid) {
	if($('#'+objid).css('display') == 'none') {
		$('#'+objid).show();
	}else {
		$('#'+objid).hide();
	}
}

//读写cookie函数
function GetCookie(c_name) {
	if (document.cookie.length > 0) {
		c_start = document.cookie.indexOf(c_name + "=");
		if (c_start != -1) {
			c_start = c_start + c_name.length + 1;
			c_end   = document.cookie.indexOf(";",c_start);
			if (c_end == -1) {
				c_end = document.cookie.length;
			}
			return unescape(document.cookie.substring(c_start,c_end));
		}
	}
	return null
}

function SetCookie(c_name,value,expiredays) {
	var exdate = new Date();
	exdate.setDate(exdate.getDate() + expiredays);
	document.cookie = c_name + "=" +escape(value) + ';path=/' +((expiredays == null) ? "" : ";expires=" + exdate.toGMTString()); //使设置的有效时间正确。增加toGMTString()
}

/* 设置模板样式 */
function setTheme(name) {
	var theme = GetCookie('MyUnoticeTheme');
	var cssUrl = base_url()+'static/css/style_'+name+'.css';
	if(theme != null) {
		$('#setTheme_'+theme).attr('class', 'skin_'+theme);
	}else {
		$('#setTheme_blue').attr('class', 'skin_blue');
	}
	$('#setTheme_'+name).attr('class', 'skin_'+name+'_selected');
	SetCookie('MyUnoticeTheme', name, 365);

	$('#themeCSS').attr('href', cssUrl);
}

/* 自动调用样式 */
function autoTheme() {
	var theme = GetCookie('MyUnoticeTheme');
	if(theme != null && __CID != 1408) {
		var cssUrl = base_url()+'static/css/style_'+theme+'.css';
		$('#setTheme_'+theme).attr('class', 'skin_'+theme+'_selected');
	}else {
		if(__CID == 1408) {
			$('#setTheme_blue').attr('class', 'skin_red_selected');
			var cssUrl = base_url()+'static/css/style_red.css';
		}else {
			$('#setTheme_blue').attr('class', 'skin_blue_selected');
			var cssUrl = base_url()+'static/css/style_blue.css';
		}
	}
	
	$('#themeCSS').attr('href', cssUrl);
}

/*时间戳转换*/
function strDate2Timestamp(strDate){
	//var	str="2007-2-28 10:18:30";
	var	strArray=strDate.split(" ");
	var	strDate=strArray[0].split("-");
	var	strTime=strArray[1].split(":");
	return new Date(strDate[0],(strDate[1]-parseInt(1)),strDate[2],strTime[0],strTime[1],strTime[2]).getTime();
}

//切换绑定的微博账号
function doActiveAccount(uid) {
	loading();
	$.ajax({
		type: "POST",
		url: site_url('client/home/do_active'),
		data: "uid="+uid,
		//dataType: 'json',
		success: function(res) {
			if(res == 'OK') {
				window.location = window.location;
			}else {
				alert(result[1]);
				unloading();
				return false;
			}
		}
	});
}

/* add by zhangbaohua for guangdong search engine on 2012-10-09*/
$(document).ready(function(){
	$('.search_more').click(function(){
		var _ifr = show_iframe();
		_ifr.attr('src',$('#search_form_guangdong').attr('action')+'?ref='+$('#gd_ref').val());
	});
	$('#search_form_guangdong').submit(function(){
		if(	is_IE) {
			document.charset='utf-8';
		}
		show_iframe();
	});
	function show_iframe(){
		var _iframe_search = '<div class="main_iframe"><iframe name="search_engine_result" id="search_engine_result" frameborder="0" width="100%" height="100%" marginheight="0" marginwidth="0" scrolling="no" ></iframe></div>'
		if($('.main_iframe').length > 0){ 
			$('.main, .main2, .main3').hide();
			$('.main_iframe').show();
		}else {
			$('.main, .main2, .main3').hide().before(_iframe_search);
		}
		return $('#search_engine_result');
	}
	//全选
	$('.search_option').find('input[type=checkbox]').click(function(){
		if ($(this).attr('class')=='all') {
			$('.op_site').find('input[type=checkbox]').attr('checked', $(this).attr("checked"));
		}else if(!$(this).attr("checked")){
			$('.search_option .all').attr('checked', false);
		}
	});
	// action for qihoo
	$('.site_type').change(function(){
		$('.op_site').hide();
		$('.op_'+$(this).val()).show();
	}).trigger('change');
});
function resizeIframe(dyHeight){
	$('.main_iframe').height(dyHeight);
	if(is_IE && document.charset!='gbk'){
		document.charset='gbk';
	}
}
