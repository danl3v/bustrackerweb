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
var previousPosts;
var cursorTimeout;
var pageX;
var pageY;
var isActive;

/* Methods */

var initLayout;
var adjustLayout;
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
	$('#map').height(documentHeight);
	$('#news-feed-background').css('width', newsFeedWidth + '%');
	$('#news-feed-background').css('height', documentHeight);
	clearTimeout(timer);
	timer = setTimeout(showScrollBars, 1000);
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
	if (isActive) {	
		$('#wrapper').fadeOut('slow');
		$('#banner').fadeIn('slow');
	}
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
	$('#footer-content, .header1-right button').fadeOut('slow');
}

/* Scroll Bars */

function showScrollBars() {
	document.documentElement.style.overflow = 'auto';
	clearTimeout(timer);
}

/* View Model */

var vm = new viewModel();
ko.applyBindings(vm);
vm.loadStops();
vm.loadLines();
vm.loadSettings();

/* Document Ready */

$(document).ready(function() {
	hideExtras();
	adjustLayout();
	initLayout();
	isActive = true;
	
	$([window, document]).focus(function() { isActive = true; }).blur(function() { isActive = false; });
	
	$(document).mousemove(function(event) {
		if (isActive && (pageX !== event.pageX || pageY !== event.pageY)) {
			hardHideBanner();
			$('*').css('cursor', 'auto');
			$('#footer-content, .header1-right button').fadeIn('slow');
			clearTimeout(cursorTimeout);
			cursorTimeout = setTimeout(hideExtras, 3000);
		}
		else if ($('#banner').length) {
			hideBanner();
		}
		pageX = event.pageX;
		pageY = event.pageY;
	});

	window.onresize = function() { adjustLayout(); };
});