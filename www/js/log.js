// needs dom.js and window.js

var Log_timeout;

function Log(message, success) {
	if (message == "")
		return;

	if (!document.body)
		return;

	// first remove previous logs
	RemoveLog()

	var classname = 'log_message';
	if (!success)
		classname = 'log_error';

	message = message.replace(/ /g, '&nbsp;');
	message = message.replace(/\n/g, '<br />\n');
	log = $c('div', {className: classname, id: 'log', innerHTML: message})

	document.body.appendChild(log)
	_top = getStyle('log', 'top')
	log.style.top = _top
	width = parseInt(getStyle('log', 'width'));
	windowWidth = WindowWidth();
	log.style.left = "" + (windowWidth/2 - width/2) + "px";

	value = 9;
	log.style.opacity = value/10;
	log.style.filter = 'alpha(opacity=' + value*10 + ')';

	// remove on click
	log.onclick = RemoveLog

	if (success)
		Log_timeout = setTimeout("FadeLog(" + value + ")", 2000)
	else
		log.innerHTML += "<br /><small>Click to close</small>";
}

function RemoveLog() {
	log = document.getElementById('log')
	if (log != null) {
		clearTimeout(Log_timeout)
		document.body.removeChild(log)
	}
}

function FadeLog(value) {
	log = document.getElementById('log')
	value--;
	if (value > 0) {
		log.style.opacity = value/10;
		log.style.filter = 'alpha(opacity=' + value*10 + ')';
		Log_timeout = setTimeout("FadeLog(" + value + ")", 50)
	} else {
		RemoveLog(log)
	}
}

// from: http://www.elektronaut.no/articles/2006/06/07/computed-styles
// Get the computed css property
function getStyle(element, cssRule)
{
	if (typeof element == 'string')
		element = document.getElementById(element)

	if (document.defaultView && document.defaultView.getComputedStyle) {
		// don't call replace with a function, won't work in safari
		prop = cssRule.replace(/([A-Z])/g, "-$1");
		prop = prop.toLowerCase();
		var style = document.defaultView.getComputedStyle(element, '');
		// style will be null if element isn't visible (not added to
		// document)
		if (style == null)
			return

		var value = style.getPropertyValue(prop);
	}
	else if (element.currentStyle) var value = element.currentStyle[cssRule];
	else                           var value = false;
	return value;
}


