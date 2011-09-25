var timer;
var bannerTimer;
var previous_predictions;
var cursorTimeout;
var pageX;
var pageY;

function initLayout() {
	$('#wrapper').css('display', 'none');
	$('#header').css('width', 100 - newsFeedWidth + '%');
	$('#divider').css('left', 100 - newsFeedWidth + '%');
	$('#stop-list-container').css('width', 100 - newsFeedWidth + '%');
	$('#news-feed-list-container').css('width', newsFeedWidth + '%');
	$('#footer').css('width', 100 - newsFeedWidth + '%');
}

function adjustLayout() {
	var documentHeight;
	document.documentElement.style.overflow = 'hidden';
	$('#divider').height(0);
	$('#news-feed-background').css('width', 0);
	documentHeight = $(document).height() - 1;
	$('#divider').height(documentHeight);
	$('#news-feed-background').css('width', newsFeedWidth + '%');
	$('#news-feed-background').css('height', documentHeight);
	clearTimeout(timer);
	timer = setTimeout("showScrollBars()", 1000);
}

function getPredictions() {
	$.get('/predictions', function(predictions) {
		if (predictions != previous_predictions) {
			$('#stop-list').fadeOut('fast', function() {
				$('#stop-list').html(predictions);
				$('#stop-list').fadeIn('fast', function() { adjustLayout(); });			
			});
			previous_predictions = predictions;
		}
	});
	setTimeout("getPredictions()", 20000);
}

function showBanner() {
	$('#wrapper').fadeOut('slow');
	$('#banner').fadeIn('slow');
	clearTimeout(bannerTimer);
	bannerTimer = setTimeout("hideBanner()", 5000);
}

function hideBanner() {
	hardHideBanner();
	bannerTimer = setTimeout("showBanner()", 20000);
}

function hardHideBanner() {
	$('#wrapper').fadeIn('slow');
	$('#banner').fadeOut('slow');
	clearTimeout(bannerTimer);
}

function showScrollBars() {
	document.documentElement.style.overflow = 'auto';
	clearTimeout(timer);
}

function hideExtras() {
	$('*').css('cursor', 'none');
	$('#footer-content').fadeOut('slow');
}

$(document).ready(function() {
	hideExtras();
	getPredictions();
	adjustLayout();
	initLayout();
	
	$(window).blur(function() { hardHideBanner(); }).focus(function() { setTimeout("hideBanner()", 500); });
	
	$(document).mousemove(function(event) {
		if (pageX != event.pageX || pageY != event.pageY) {
			hardHideBanner();
			$('*').css('cursor', 'auto');
			$('#footer-content').fadeIn('slow');
			clearTimeout(cursorTimeout);
			cursorTimeout = setTimeout('hideExtras()', 1000);
		}
		else {
			hideBanner();
		}
		pageX = event.pageX;
		pageY = event.pageY;
	});

	window.onresize = function(event) { adjustLayout(); };
});