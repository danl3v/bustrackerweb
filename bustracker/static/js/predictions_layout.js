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
var isActive;

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

/* Data to represent returned data */

var stop = function(aStop)
{
	var self = this;
	
	if (aStop) {
		this.id = ko.observable(aStop.id);
		this.title = ko.observable(aStop.title);
		
		this.agencyChoice = ko.observable(vm.agencyFromTag(aStop.agencyTag));
		
		this.agencyTag = ko.observable(aStop.agencyTag);
		this.lineTag = ko.observable(aStop.lineTag);
		this.directionTag = ko.observable(aStop.directionTag);
		this.stopTag = ko.observable(aStop.stopTag);
		this.destinationTag = ko.observable(aStop.destinationTag);
		
		this.timeToStop = ko.observable(aStop.timeToStop);
		this.directions = ko.observableArray([]);
		this.position = ko.observable(aStop.position);
	}
	else {
		this.id = ko.observable(null);
		this.title = ko.observable("");
		
		this.agencyChoice = ko.observable(null);
		
		this.agencyTag = ko.observable("");
		this.lineTag = ko.observable("");
		this.directionTag = ko.observable("");
		this.stopTag = ko.observable("");
		this.destinationTag = ko.observable("");
		
		this.timeToStop = ko.observable(0);
		this.directions = ko.observableArray([]);
		this.position = ko.observable(0);
	}
}

var direction = function(timeToStop, title, destinations)
{
	this.title = ko.observable(title);
	this.destinations = ko.observableArray([]);
	
	var mappedDestinations = $.map(destinations, function(aDestination) {
		return new destination(timeToStop, aDestination.title, aDestination.vehicles);
	});
	this.destinations(mappedDestinations);
}

var destination = function(timeToStop, title, vehicles)
{
	this.direction = ko.observable(direction);
	this.title = ko.observable(title);
	this.vehicles = ko.observableArray([]);
	
	var mappedVehicles = $.map(vehicles, function(aVehicle) {
		return new vehicle(timeToStop, aVehicle.minutes);
	});
	this.vehicles(mappedVehicles);
}

var vehicle = function(timeToStop, minutes)
{
	this.destination = ko.observable(destination);
	this.minutes = ko.observable(minutes);
	this.timeToLeave = ko.observable(minutes - timeToStop());
	
	if (this.timeToLeave() < 0) {
		this.prettyTimeToLeave = "missed";
	}
	else if (this.timeToLeave() == 0) {
		this.prettyTimeToLeave = "leave now";
	}
	else if (this.timeToLeave() == 1) {
		this.prettyTimeToLeave = "leave in 1m";
	}
	else {
		this.prettyTimeToLeave = "leave in " + this.timeToLeave().toString() + "m";
	}
}

var selectionChoice = function(title, tag) {
	this.title = title;
	this.tag = tag;
}

/* View Model */

var viewModel = function() {
	var self = this;
	
	this.isLoading = ko.observable(false);
	this.stops = ko.observableArray([]);
	this.editingStop = ko.observable(false);
	
	this.agencyFromTag = function(tag) {
		var theChoice = null;
		self.agencyChoices.forEach(function(anAgencyChoice, i) {
			if (anAgencyChoice.tag == tag) {
				theChoice = anAgencyChoice;
			}
		});
		return theChoice;
	};
	
	this.stopWithId = function(id) {
		var stopToReturn = null;
		self.stops().forEach(function(aStop, i) {
			if (aStop.id() == id) {
				stopToReturn = aStop;
			}
		});
		return stopToReturn;
	};
	
	// stop actions
	this.moveup = function(i) {
		if (i > 0) {
			stop = self.stops()[i];
			self.stops.splice(i, 1);
			self.stops.splice(i-1, 0, stop);
		}
	};
	
	this.movedown = function(i) {
		if (i < self.stops().length) {
			stop = self.stops()[i];
			self.stops.splice(i, 1);
			self.stops.splice(i+1, 0, stop);
		}
	};
	
	this.edit = function(i) {
		self.editingStop(self.stops()[i]);
	}
	
	this.new = function() {
		self.stops.push(new stop(null));
		self.editingStop(self.stops()[self.stops().length-1]);
	}
	
	this.delete = function(i) {
		if (confirm("Do you really want to delete this stop?")) {
			self.stops.splice(i, 1);
		}
	}
	
	// board actions
	this.loadStops = function() {
		self.isLoading = true;
		$.get("/stops", function(stops) {
			var mappedStops = $.map(stops, function(aStop, index) {
				return new stop(aStop);
			});
			self.stops(mappedStops);
			self.isLoading = false;
			self.refresh();
		}, 'json');
	
	}
	
	this.refresh = function() {
		$.get("/predictions", function(predictions) {
			$.map(predictions, function(aPrediction, i) {
				var mappedDirections = $.map(aPrediction.directions, function(aDirection) {
					return new direction(self.stops()[i].timeToStop, aDirection.title, aDirection.destinations);
				});
				self.stopWithId(aPrediction.id).directions(mappedDirections);
			});
		}, 'json');
		setTimeout(self.refresh, 20000);	
	}
	
	// selections
	this.agencyChoices = [];
	this.lineChoices = [];
	
	this.updateAgencyChoices = function() {
		$.get("/agencies", function(agencies) {
			var mappedAgencies = $.map(agencies, function(anAgency, index) {
				return new selectionChoice(anAgency.title, anAgency.tag);
			});
			self.agencyChoices = mappedAgencies;
		}, 'json');
	};
	
	this.updateLineChoices = function() {
		$.get("/actransit/lines", function(lineChoices) {
			var mappedLineChoices = $.map(lineChoices, function(aLineChoice, index) {
				return new selectionChoice(aLineChoice.title, aLineChoice.tag);
			});
			self.lineChoices = mappedLineChoices;
		}, 'json');
	};
	
	this.updateAgencyChoices();
	this.updateLineChoices();
};

var vm = new viewModel();
ko.applyBindings(vm);
vm.loadStops();

/* Document Ready */

$(document).ready(function() {
	hideExtras();
	//getPredictions();
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
			cursorTimeout = setTimeout(hideExtras, 1000);
		}
		else if ($('#banner').length) {
			hideBanner();
		}
		pageX = event.pageX;
		pageY = event.pageY;
	});

	window.onresize = function() { adjustLayout(); };
});