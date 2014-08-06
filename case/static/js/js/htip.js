/*
 * HTip
 * By Laurence.xu (http://www.haohailuo.com)
 * HTip is built on top of the very light weight jquery library.
 */
var ht_timer;
var ht_timer0;

function Htips(obj, sourceIdPre) {
	var width = 300;
	var opacity = 1;
	var html = "<div id='HTip' ref='forbid' style='display:none;width:"+width+"px;opacity:"+opacity+";'><div class='Htip-jiantouLeft' id='Htip-jiantou'></div>";
	html += '<div class="Htip"><div class="Htip-borderTop"><div class="Htip-Lcanvas"></div><div class="Htip-Rcanvas"></div><div style="width:'+(width-8)+'px;" id="Htip-betweenCorners-top" class="Htip-betweenCorners">&nbsp;</div>';
	html += '</div><div class="Htip-contentWrapper"><div class="Htip-title"><a title="Close" id="Htip-close" class="Htip-close">&nbsp;</a><div id="Htitle">ндубу╙р╙</div></div><div id="Htip-content" class="Htip-content"></div></div>';
	html += '<div class="Htip-borderBottom"><div class="Htip-Lcanvas"></div><div class="Htip-Rcanvas"></div><div style="width:'+(width-8)+'px;" id="Htip-betweenCorners-down" class="Htip-betweenCorners">&nbsp;</div></div></div></div>';
	
	$("body").append(html);
	$('#Htip-jiantouLeft').css('height', $('#HTip').height());
	$('#Htip-close').click(function(){hideHtips(1)});
	
	var el = $(obj);
	
	if(el.attr('id') == '') {
		el.attr('id',"ht_" + Math.round(Math.random()*100000));
	}
	
	var h = el.attr('href') || el.attr('ref'); 
	var i = el.attr('id'); 
	var n = el.attr('title') || el.attr('name');
	
	clearTimeout(ht_timer0);
	
	$('.Htip-vspib').each(function(){
		$(this).removeClass('Htip-vspib-hover');
		if($(this).attr('id') == 'vspib_'+i) {
			$(this).addClass('Htip-vspib-hover');
		}
	});
	$('#Htip-content').html("Loading...");

	o = el.offset();
	var ewidth = el.width();
	ewidth = ewidth > 10 ? ewidth : 10;
	
	var de = document.documentElement;
	var w = self.innerWidth || (de && de.clientWidth) || document.body.clientWidth;
	var hasArea = w - o.left - ewidth;
	
	if(hasArea > width || o.left < width+10) {
		$('#Htip-jiantou').attr('class', 'Htip-jiantouLeft');
		$('#HTip').css({
			'top': o.top - 12,
			'left': o.left+15+ewidth
		});
	}else if(o.left > width+10) {
		$('#Htip-jiantou').attr('class', 'Htip-jiantouRight');
		$('#HTip').css({
			'top': o.top - 12,
			'left': o.left-15-width
		});
	}else {
		$('#Htip-jiantou').attr('class', 'Htip-jiantouLeft');
		$('#HTip').css({
			'top': o.top - 12,
			'left': o.left+15+ewidth
		});
	}
	
	ht_timer0 = setTimeout(function(){ showHtips(h, i, n, sourceIdPre) } , 500);
}

function showHtips(url, Id, title, sourceIdPre) {
	$('#Htip-content').html("Loading...");
	$('#HTip').fadeIn();
	
	var sourceId = '';
	if(sourceIdPre) {
		sourceId = sourceIdPre+'_'+Id;
	}
	
	if (title) {
		$('#Htitle').html(title);
	}
	
	if(sourceId != '') {
		$('#Htip-content').html($('#'+sourceId).html());
	}else {
		$('#Htip-content').load(url);
	}
}

function hideHtips(is_forbid) {
	clearTimeout(ht_timer);
	clearTimeout(ht_timer0);
	ht_timer = setTimeout( function(){
		$('#HTip').fadeOut();
		$('.Htip-vspib').removeClass('Htip-vspib-hover');
	}, 300);
}
