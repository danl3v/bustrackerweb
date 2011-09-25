var timer;
var bannerTimer;
var previous_predictions;

function initLayout(newsFeedWidth) {
	$('#header').css('width', 100 - newsFeedWidth + '%');
	$('#divider').css('left', 100 - newsFeedWidth + '%');
	$('#stop-list-container').css('width', 100 - newsFeedWidth + '%');
	$('#news-feed-list-container').css('width', newsFeedWidth + '%');
	$('#footer').css('width', 100 - newsFeedWidth + '%');
}

function adjustLayout(newsFeedWidth) {
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
				$('#stop-list').fadeIn('fast');			
			});
		}
		else {
			$('#stop-list').html(predictions);
		}
		previous_predictions = predictions;
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
	$('#wrapper').fadeIn('slow');
	$('#banner').fadeOut('slow');
	clearTimeout(bannerTimer);
	bannerTimer = setTimeout("showBanner()", 20000);
}

function showScrollBars() {
	document.documentElement.style.overflow = 'auto';
	clearTimeout(timer);
}

$(document).ready(function() {
	getPredictions();
	$('#wrapper').css('display', 'none');
});