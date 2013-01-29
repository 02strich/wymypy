function $(id) {
	return document.getElementById(id);
}

function set_cursor(t) {
	 //var cursor =
	 //document.layers ? document.cursor :
	 //document.all ? document.all.cursor :
	 //document.getElementById ? document.getElementById('cursor') : null;
	 document.body.style.cursor = t;
 }

var sajax_debug_mode = false;

function sajax_debug(text) {
	if (sajax_debug_mode)
		alert("RSD: " + text)
}

function sajax_init_object() {
	sajax_debug("sajax_init_object() called..")
	
	var A;
	try {
		A = new ActiveXObject("Msxml2.XMLHTTP");
	} catch (e) {
		try {
			A = new ActiveXObject("Microsoft.XMLHTTP");
		} catch (oc) {
			A = null;
		}
	}
	if(!A && typeof XMLHttpRequest != "undefined")
		A = new XMLHttpRequest();
	if (!A)
		sajax_debug("Could not create connection object.");
	return A;
}

function sajax_do_call( url, args) {
	set_cursor('wait');
	var i, x, n, data="";
	for (i = 0; i < args.length; i++) {
		if(data!="") data+="&";
		data = data + "p"+i+"=" + encodeURIComponent(args[i]);
	}
	x = sajax_init_object();
	x.open("POST", url, true);
	x.setRequestHeader("Method", "POST " + url + " HTTP/1.1");
	x.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
	x.onreadystatechange = function() {
		if (x.readyState != 4)
			return;
		sajax_debug("received " + x.responseText);
		
		set_cursor('default');
		var status;
		var data;
		status = x.responseText.charAt(0);
		data = x.responseText.substring(2);
		if (status == "-")
			alert("Error: " + data);
		else {
			// data is a json dict
			var obj = eval("(" + data + ")");
			for(var id in obj) {
				var target = $(id)
				if(target)
					target.innerHTML = obj[id];
			}
		}
	}
	x.send(data);
	sajax_debug(" url = " + url);
	sajax_debug(" waiting..");
	delete x;
}

function refresh(isForced)
{
	ajax_player(isForced);
	
	if($("timer"))
		var v = $("timer").value;
	else
		var v = "5000"
	
	if(v != "")
		_timer = window.setTimeout('refresh()', parseInt(v));
}

function seekclick(e)
{
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

function changeDisplay(elt)
{
	ajax_ope("changeDisplay",(elt.checked?"1":"0"));
}

function init()
{
	// ajax_liste("");
	refresh(1);
}
