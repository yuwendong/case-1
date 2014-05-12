$('#TopicTabContent :checkbox').click(function(){
    var $this = $(this);
    if ($this.is(':checked')) {
	$.each($('#TopicTabContent :checkbox'), function(i, val) {
	    if ($(this) != $this) {
		$(this).attr('checked', false);
	    }
	});
	$this.attr('checked', true);
	var topic_str = $this.parent().text().replace(/^\s+|\s+$/g,'');
        $('#topic_keywords').val(topic_str);
    } else {
	$this.attr('checked', false);
        var topic_str = $this.parent().text().replace(/^\s+|\s+$/g,'');
	var current_val = $('#topic_keywords').val();
	current_val = current_val.replace(topic_str, '');
        $('#topic_keywords').val(current_val);
    }
})