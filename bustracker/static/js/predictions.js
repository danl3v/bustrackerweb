/* 
 * predictions.js
 * TrackMyBus
 */

/*global document, window, setTimeout, clearTimeout, $ */
/*jslint browser: true, undef: true, sloppy: true, eqeq: true, white: true, maxerr: 50, indent: 4 */


/* Variables */
var timer;
var newsFeedWidth;
var bannerTimer;
var previousPredictions;
var previousPosts;
var cursorTimeout;
var pageX;
var pageY;

/* Methods */

var initLayout;
var adjustLayout;
var getPredictions;
var showBanner;
var hideBanner;
var hardHideBanner;
var hideExtras;
var showScrollBars;

/* Layout */

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
	timer = setTimeout(showScrollBars, 1000);
}

/* Predictions */

function getPredictions() {
	$.get('/predictions', function(predictions) {
		if (predictions !== previousPredictions) {
			$('#stop-list').fadeOut('fast', function() {
				$('#stop-list').html(predictions);
				$('#stop-list').fadeIn('fast', function() { adjustLayout(); });			
			});
			previousPredictions = predictions;
		}
	});
	setTimeout(getPredictions, 20000);
}

/* Posts */

function getPosts() {
	$.get('/posts', function(posts) {
		if (posts !== previousPosts) {
			$('#news-feed-list').fadeOut('fast', function() {
				$('#news-feed-list').html(posts);
				$('#news-feed-list').fadeIn('fast', function() { adjustLayout(); });
			});
			previousPosts = posts;
		}
	});
	setTimeout(getPosts, 60000);
}

/* Banner */

function showBanner() {
	$('#wrapper').fadeOut('slow');
	$('#banner').fadeIn('slow');
	clearTimeout(bannerTimer);
	bannerTimer = setTimeout(hideBanner, 5000);
}

function hideBanner() {
	hardHideBanner();
	bannerTimer = setTimeout(showBanner, 20000);
}

function hardHideBanner() {
	$('#wrapper').fadeIn('slow');
	$('#banner').fadeOut('slow');
	clearTimeout(bannerTimer);
}

/* Hiding Footer and Cursor */

function hideExtras() {
	$('*').css('cursor', 'none');
	$('#footer-content').fadeOut('slow');
}

/* Scroll Bars */

function showScrollBars() {
	document.documentElement.style.overflow = 'auto';
	clearTimeout(timer);
}

/* Document Ready */

$(document).ready(function() {
	hideExtras();
	getPredictions();
	adjustLayout();
	initLayout();
	
	$(window).blur(function() { hardHideBanner(); }).focus(function() { setTimeout(hideBanner, 500); });
	
	$(document).mousemove(function(event) {
		if (pageX !== event.pageX || pageY !== event.pageY) {
			hardHideBanner();
			$('*').css('cursor', 'auto');
			$('#footer-content').fadeIn('slow');
			clearTimeout(cursorTimeout);
			cursorTimeout = setTimeout(hideExtras, 1000);
		}
		else {
			hideBanner();
		}
		pageX = event.pageX;
		pageY = event.pageY;
	});

	window.onresize = function() { adjustLayout(); };
});