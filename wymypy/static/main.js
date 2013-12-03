function seekclick(e) {
	var x;
	if(e.offsetX)
		x=e.offsetX
	else
	{
		var Element = e.target ;
		var CalculatedTotalOffsetLeft = CalculatedTotalOffsetTop = 0 ;
		while (Element.offsetParent)
		{
			CalculatedTotalOffsetLeft += Element.offsetLeft ;
			CalculatedTotalOffsetTop += Element.offsetTop ;
			Element = Element.offsetParent ;
		}

		OffsetXForNS6 = e.pageX - CalculatedTotalOffsetLeft ;
		OffsetYForNS6 = e.pageY - CalculatedTotalOffsetTop ;
		x=OffsetXForNS6;
	}

	ajax_ope("seek",Math.round(x/2));
}

function audio_playstop() {
	if($("#stream_player_audio").length) {
		//$("#stream_player_audio").pause();
		$("#stream_player_audio").remove();
	} else {
		$("#stream_player").append("<audio id='stream_player_audio' src='" + $("#stream_player").data('stream-src') + "?" + new Date().getTime() + "' autoplay controls></audio>");
	}

	return false;
}

function refresh_player() {
	$.ajax({
		type: "POST",
		url: "/plugin/player",
		complete: function(jqXHR, textStatus) {
			$("#zone_player").html(jqXHR.responseText);
		}
	});

	$.ajax({
		type: "POST",
		url: "/plugin/player/playlist",
		complete: function(jqXHR, textStatus) {
			$("#zone_playList").html(jqXHR.responseText);
		}
	});
}

function refresh_player_loop(isForced) {
	refresh_player();
	
	var v = $("#timer").val();

	if(v != "")
		_timer = window.setTimeout(refresh_player_loop, parseInt(v));
}

function load_plugin_content(plugin_name, action, parameters) {
	$.ajax({
		type: "POST",
		url: "/plugin/" + plugin_name + ((action == "index") ? "" : ("/" + action)),
		data: parameters,
		complete: function(jqXHR, textStatus) {
			$("#zone_plugins").html(jqXHR.responseText);
		}
	});
}

function execute_plugin(plugin_name, action, parameters, complete_handler) {
	complete_handler = typeof complete_handler !== 'undefined' ? complete_handler : function(jqXHR, textStatus) {};

	$.ajax({
		type: "POST",
		url: "/__ajax/" + plugin_name + ((action == "index") ? "" : ("/" + action)),
		data: parameters,
		complete: complete_handler
	});	
}
