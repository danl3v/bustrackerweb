/* 
 * model.js
 * TrackMyBus
 */

var map;
var saveMapDefaultsTimer;
var vm;
var isMobile;

/* KO ADDONS */

ko.protectedObservable = function(initialValue) {
	var _actualValue = ko.observable(initialValue);
	var _tempValue = initialValue;
	
	var result = ko.dependentObservable({
		read: function() {
		   return _actualValue(); 
		},

		write: function(newValue) {
			 _tempValue = newValue; 
		}
	}); 
	

	result.commit = function() {
		if (_tempValue !== _actualValue()) {
			 _actualValue(_tempValue); 
		}  
	};
	
	result.reset = function() {
		_actualValue.valueHasMutated();
		_tempValue = _actualValue();
	};
 
	return result;
};

/* HELPERS */

function getAnchor(angle) {
	switch (angle) {
		case 0:
			return new google.maps.Point(18, 18)
			break;
		case 45:
			return new google.maps.Point(26, 27)
			break;
		case 90:
			return new google.maps.Point(18, 18)
			break;
		case 135:
			return new google.maps.Point(27, 48)
			break;
		case 180:
			return new google.maps.Point(18, 49)
			break;
		case -135:
			return new google.maps.Point(48, 48)
			break;
		case -90:
			return new google.maps.Point(49, 18)
			break;
		case -45:
			return new google.maps.Point(48, 27)
			break;
	}
}

var colorList = function() {
	var self = this;
	this.i = 0;
	this.colors = ["#FFAD29", "#5CE1FF", "#A89CFF", "#FF4FA7", "#FFF129", "#45FF70", "#C23C3C"];
	this.color = function() {
		self.i++;
		return self.colors[self.i % self.colors.length];
	};
};

var aColorList = new colorList();

/* CLASSES */

var line = function(aLine) {

	var self = this;
	this.agencyTag = aLine.agencyTag;
	this.lineTag = aLine.lineTag;
	this.color = aColorList.color();
	this.polyLineList = [];
	this.vehicles = ko.observableArray([]);
	
	this.undraw = function() {
		for (var i=0; i < self.polyLineList.length;i++) {
			self.polyLineList[i].setMap(null);
		}
		for (var i=0; i < self.vehicles().length;i++) {
			self.vehicles()[i].undraw();
		}
	};

	this.draw = function() {
	
		for (var i=0; i < aLine.paths.length;i++) {
			var coordinates = [];
			
			for (var j=0; j < aLine.paths[i].length;j++) {
				coordinates.push(new google.maps.LatLng(aLine.paths[i][j].lat, aLine.paths[i][j].lon));
			}
			
			var polyLineCasing = new google.maps.Polyline({
				path: coordinates,
				strokeColor: "#000000",
				strokeOpacity: 1.0,
				strokeWeight: 10
			});
			polyLineCasing.setMap(map);
			self.polyLineList.push(polyLineCasing);
			
			var polyLineInside = new google.maps.Polyline({
				path: coordinates,
				strokeColor: self.color,
				strokeOpacity: 1.0,
				strokeWeight: 5
			});
			polyLineInside.setMap(map);
			self.polyLineList.push(polyLineInside);
		}
	};
	
	this.vehicleFromId = function(id) {
		var theVehicle = null;
		self.vehicles().forEach(function(aVehicle, i) {
			if (aVehicle.id == id) {
				theVehicle = aVehicle;
			}
		});
		return theVehicle;
	};
	
	this.draw();
};

var stop = function(aStop) {
	var self = this;
	this.marker = null;

	if (aStop != null) {
		this.id = ko.observable(aStop.id);
		this.title = ko.protectedObservable(aStop.title);
		this.lat = ko.observable(aStop.lat);
		this.lon = ko.observable(aStop.lon);
		this.timeToStop = ko.protectedObservable(aStop.timeToStop);
		this.isEditable = ko.observable(aStop.isEditable);
		
		this.agencyTag = aStop.agencyTag;
		this.lineTag = aStop.lineTag;
		this.directionTag = aStop.directionTag;
		this.stopTag = aStop.stopTag;
	}
	else {
		this.id = ko.observable();
		this.title = ko.protectedObservable("untitled stop");
		this.lat = ko.observable(0);
		this.lon = ko.observable(0);
		this.timeToStop = ko.protectedObservable(0);
		this.isEditable = ko.observable(true);
		
		this.agencyTag = null;
		this.lineTag = null;
		this.directionTag = null;
		this.stopTag = null;
	}

	this.title.subscribe(function(newValue) {
		self.updateMarker();
	});
	
	this.lat.subscribe(function(newValue) {
		self.updateMarker();
	});
	
	this.lon.subscribe(function(newValue) {
		self.updateMarker();
	});
	
	this.commitAll = function() {
		self.title.commit();
		self.timeToStop.commit();
		
		self.agencyTag = self.agencyChoice().tag;
		self.lineTag = self.lineChoice().tag;
		self.directionTag = self.directionChoice().tag;
		self.stopTag = self.stopChoice().tag;
	};
	
	this.resetAll = function() {
		self.title.reset();
		self.timeToStop.reset();
		
		this.agencyChoices([]);
		this.lineChoices([]);
		this.directionChoices([]);
		this.stopChoices([]);
		
		this.agencyChoice(null);
		this.lineChoice(null);
		this.directionChoice(null);
		this.stopChoice(null);
		
		self.canUpdateChoices(true);
		self.trigger(!self.trigger());
	};
	
	this.undraw = function() {
		if (self.marker) {
			self.marker.setMap(null);
			self.marker = null;
		}
	};
	
	this.updateMarker = function() {

		var image = new google.maps.MarkerImage('https://chart.googleapis.com/chart?chst=d_bubble_texts_big&chld=bb|000000|FFFFFF|' + self.title(),
				null, // size
				new google.maps.Point(0,0), // origin
				new google.maps.Point(0, 59) // anchor
			);
		
		if (self.marker) {
			self.marker.setPosition(new google.maps.LatLng(self.lat(), self.lon()));
			self.marker.setIcon(image);
		}
		else {
			self.marker = new google.maps.Marker({
				position: new google.maps.LatLng(self.lat(), self.lon()),
				map: map,
				icon: image
			});
		}
	};
	
	this.updateMarker();
	
	this.agencyChoices = ko.observableArray([]);
	this.lineChoices = ko.observableArray([]);
	this.directionChoices = ko.observableArray([]);
	this.stopChoices = ko.observableArray([]);
	
	this.agencyChoice = ko.observable(null);
	this.lineChoice = ko.observable(null);
	this.directionChoice = ko.observable(null);
	this.stopChoice = ko.observable(null);
	
	this.directions = ko.observableArray([]);
	
	// choiceFromTag
	this.choiceFromTag = function(tag, choices) {
		var theChoice = null;
		choices.forEach(function(aChoice, i) {
			if (aChoice.tag == tag) {
				theChoice = aChoice;
			}
		});
		return theChoice;
	};
	
	this.canUpdateChoices = ko.observable(true);
	this.trigger = ko.observable(true);
	
	// choice updating functions
	this.updateAgencyChoices = ko.dependentObservable(function() {
		$.get("/agencies", function(agencyChoices) {
			var mappedAgencyChoices = $.map(agencyChoices, function(anAgency, index) {
				return new selectionChoice(anAgency.title, anAgency.tag);
			});
			self.agencyChoices(mappedAgencyChoices);
			if (self.agencyTag && self.canUpdateChoices()) {
				self.agencyChoice(self.choiceFromTag(self.agencyTag, mappedAgencyChoices));
			}
		}, 'json');
		return self.trigger();
	}, this);
	
	this.updateLineChoices = ko.dependentObservable(function() {
		self.lineChoice(null);
		self.lineChoices([]);
		if (self.agencyChoice()) {
			$.get("/" + self.agencyChoice().tag + "/lines", function(lineChoices) {
				if (lineChoices[0] == "error") {
 					alert("There has been an error updating the line choices. Please try again soon.");
 				}
 				else {
					var mappedLineChoices = $.map(lineChoices, function(aLineChoice, index) {
						return new selectionChoice(aLineChoice.title, aLineChoice.tag);
					});
					self.lineChoices(mappedLineChoices);
					if (self.lineTag && self.canUpdateChoices()) {
						self.lineChoice(self.choiceFromTag(self.lineTag, mappedLineChoices));
					}
				}
			}, 'json');
		}
		return "";
	}, this);
	
	this.updateDirectionChoices = ko.dependentObservable(function() {
		self.directionChoice(null);
		self.directionChoices([]);
		if (self.agencyChoice() && self.lineChoice()) {
			$.get("/" + self.agencyChoice().tag + "/" + self.lineChoice().tag + "/directions", function(directionChoices) {
				if (directionChoices[0] == "error") {
					alert("There has been an error updating the direction choices. Please try again soon.");
				}
				else {
					var mappedDirectionChoices = $.map(directionChoices, function(aDirectionChoice, index) {
						return new selectionChoice(aDirectionChoice.title, aDirectionChoice.tag);
					});
					self.directionChoices(mappedDirectionChoices);
					if (self.directionTag && self.canUpdateChoices()) {
						self.directionChoice(self.choiceFromTag(self.directionTag, mappedDirectionChoices));
					}
				}
			}, 'json');
		}
		return "";
	}, this);
	
	this.updateStopChoices = ko.dependentObservable(function() {
		self.stopChoice(null);
		self.stopChoices([]);
		if (self.agencyChoice() && self.lineChoice() && self.directionChoice()) {
			$.get("/" + self.agencyChoice().tag + "/" + self.lineChoice().tag + "/" + self.directionChoice().tag + "/stops", function(stopChoices) {
				if (stopChoices[0] == "error") {
					alert("There has been an error updating the stop choices. Please try again soon.");
				}
				else {
					var mappedStopChoices = $.map(stopChoices, function(aStopChoice, index) {
						return new selectionChoice(aStopChoice.title, aStopChoice.tag);
					});
					self.stopChoices(mappedStopChoices);
					if (self.stopTag && self.canUpdateChoices()) {
						self.stopChoice(self.choiceFromTag(self.stopTag, mappedStopChoices));
						self.canUpdateChoices = ko.observable(false);
					}
				}
			}, 'json');
		}
		return "";
	}, this);
};

var direction = function(stop, title, destinations) {
	var self = this;
	this.title = ko.observable(title);
	this.destinations = ko.observableArray([]);
	
	this.updateDestinations = function(destinations) {
		var mappedDestinations = $.map(destinations, function(aDestination) {
//			for (var i=0; i < self.destinations().length; i++) {
//				if (self.destinations()[i].title() == aDestination.title) { // convert this to a dependant observable?
//					var theDestination = self.destinations()[i];
//					theDestination.updateVehicles(aDestination.vehicles);
//					return theDestination;
//				}
//			}
			return new destination(stop, aDestination.title, aDestination.vehicles);
		});
		self.destinations(mappedDestinations);
	};
	this.updateDestinations(destinations);
};

var destination = function(stop, title, vehicles) {
	var self = this;
	
	this.direction = ko.observable(direction);
	this.title = ko.observable(title);
	this.vehicles = ko.observableArray([]);
	
	this.updatePredictions = function(vehicles) {
		var mappedVehicles = $.map(vehicles, function(aVehicle) {
//			for (var i=0; i < self.vehicles().length; i++) {
//				if (self.vehicles()[i].vehicleNumber == aVehicle.number) { // convert this to a dependant observable?
//					var theVehicle = self.vehicles()[i];
//					theVehicle.minutes(aVehicle.minutes);
//					return theVehicle;
//				}
//			}
			return new prediction(stop, aVehicle.minutes, aVehicle.number);
		});
		self.vehicles(mappedVehicles);
	};
	
	this.updatePredictions(vehicles);
};

var prediction = function(stop, minutes, vehicleNumber) {
	var self = this;
	
	this.vehicleNumber = vehicleNumber;
	this.minutes = ko.observable(minutes);
	
	this.minutes.subscribe(function(newValue) {
		self.updateVehicleMarker();
	});
	
	this.timeToLeave = ko.dependentObservable(function() {
		return self.minutes() - stop.timeToStop();
	}, this);

	this.prettyMinutesToArrival = ko.dependentObservable(function() {
		if (self.minutes() < 0) {
			return "Departed";
		}
		else if (self.minutes() == 0) {
			return "Arriving";
		}
		else {
			return self.minutes().toString();
		}
	}, this);
	
	this.prettyMinutesToArrivalSuffix = ko.dependentObservable(function() {
		if (self.minutes() == 1) {
			return "minute";
		}
		else if (self.minutes() > 1) {
			return "minutes";
		}
		else {
			return "";
		}
	}, this);

	this.prettyTimeToLeave = ko.dependentObservable(function() {
		if (self.timeToLeave() < 0) {
			return "missed";
		}
		else if (self.timeToLeave() == 0) {
			return "leave now";
		}
		else {
			return "leave in " + self.timeToLeave().toString() + "m";
		}
		
	}, this);
};

var vehicle = function(aVehicle, aLine) {
	var self = this;

	this.id = aVehicle.id;
	this.lat = ko.observable(aVehicle.lat);
	this.lon = ko.observable(aVehicle.lon);
	this.heading = ko.observable(aVehicle.heading);
	this.directionTag = ko.observable(aVehicle.directionTag);
	this.marker = null;
	this.isAnimating = false;

	this.directionTag.subscribe(function(newValue) {
		self.updateVehicleMarker();
	});

	this.lat.subscribe(function(newValue) {
		self.updateVehicleMarker();
	});
	
	this.lon.subscribe(function(newValue) {
		self.updateVehicleMarker();
	});
	
	this.heading.subscribe(function(newValue) {
		var roundedHeading = (Math.floor((180.0 - self.heading()) / 45.0) * 45);
		var image = new google.maps.MarkerImage('https://chart.googleapis.com/chart?chst=d_map_spin&chld=1|' + roundedHeading.toString() + '|FFFFFF|11|b|' + aLine.lineTag,
			null, // size
			new google.maps.Point(0,0), // origin
			getAnchor(roundedHeading) // anchor
		);
	
		self.marker.setIcon(image);
	});
	
	this.undraw = function() {
		if (self.marker) {
			self.marker.setMap(null);
			self.marker = null;
		}
	};
	
	this.moveToStep = function(marker, startPoint, stepCurrent, stepsTotal) {
		if (self.marker && stepCurrent < stepsTotal) {
			marker.setPosition(new google.maps.LatLng(parseFloat(startPoint.lat() + stepCurrent*((self.lat() - startPoint.lat()) / stepsTotal)), parseFloat(startPoint.lng() + stepCurrent*((self.lon() - startPoint.lng())/ stepsTotal))));
			window.setTimeout(function() {
				self.moveToStep(marker, startPoint, stepCurrent+1, stepsTotal);
			}, 200);
		}
		else {
			self.isAnimating = false;
		}
	};
	
	this.updateVehicleMarker = function() {
		if (self.marker) {
			//self.heading(90 + 180/3.1415926535 * (Math.atan2((self.lon() - self.marker.position.lng()), (self.lat() - self.marker.position.lat()))));
			if (self.isAnimating) {
				window.setTimeout(self.updateVehicleMarker, 5000);
			}
			else {
				self.isAnimating = true;
				self.moveToStep(self.marker, self.marker.position, 0, 80);
			}
		}
		else if (self.directionTag() && self.lat() != 0 && self.lon() != 0) {
			self.undraw();
			var roundedHeading = (Math.floor((180.0 - self.heading()) / 45.0) * 45);
				
			var image = new google.maps.MarkerImage('https://chart.googleapis.com/chart?chst=d_map_spin&chld=1|' + roundedHeading.toString() + '|FFFFFF|11|b|' + aLine.lineTag,
				null, // size
				new google.maps.Point(0,0), // origin
				getAnchor(roundedHeading) // anchor
			);
		
			self.marker = new google.maps.Marker({
				position: new google.maps.LatLng(self.lat(), self.lon()),
				map: map,
				title: roundedHeading.toString(),
				icon: image
			});
		}
		else if (!self.directionTag()) {
			self.undraw();
		}
	};
	this.updateVehicleMarker();
};

var selectionChoice = function(title, tag) {
	this.title = title;
	this.tag = tag;
};

/* View Model */

var viewModel = function() {
	var self = this;
	
	// wrapper
	this.showSidebar = ko.observable(true);
	
	this.toggleSidebar = function() {
		self.showSidebar(!self.showSidebar());
	};
	
	this.toggleSidebarButtonText = ko.dependentObservable(function() {
		if (self.showSidebar()) {
			return 'x';
		}
		return 'o';
	
	}, this);
	
	this.stops = ko.observableArray([]);
	this.lines = ko.observableArray([]);
	
	this.isNewStop;
	this.editingStop = ko.observable(false);
	
	this.stopWithId = function(id) {
		var stopToReturn = null;
		self.stops().forEach(function(aStop, i) {
			if (aStop.id() == id) {
				stopToReturn = aStop;
			}
		});
		return stopToReturn;
	};
	
	// move stop up or down
	this.moveup = function(i) {
		if (i > 0) {
			$.post("/stop/moveup", { "id" : self.stops()[i].id() }, function(data) {
				if (!data || !(data.id)) {
					alert("Problem updating data on server.");
				}
			}, 'json');
			stop = self.stops()[i];
			self.stops.splice(i, 1);
			self.stops.splice(i-1, 0, stop);
		}
	};
	
	this.movedown = function(i) {
		if (i < self.stops().length) {
			$.post("/stop/movedown", { "id" : self.stops()[i].id() }, function(data) {
				if (!data || !(data.id)) {
					alert("Problem updating data on server.");
				}
			}, 'json');
			stop = self.stops()[i];
			self.stops.splice(i, 1);
			self.stops.splice(i+1, 0, stop);
		}
	};
	
	// stop editing
	this.newStop = function() {
		self.isNewStop = true;
		self.editingStop(new stop(null));
	};
	
	this.editStop = function(i) {
		self.isNewStop = false;
		self.editingStop(self.stops()[i]);
	};
	
	this.cancelEditingStop = function() {
		self.editingStop().resetAll();
		self.editingStop(false);
	};
	
	this.doneEditingStop = function() {
		stop = self.editingStop();
		if (stop.agencyChoice() && stop.lineChoice() && stop.directionChoice() && stop.stopChoice()) {
			if (self.isNewStop) {
				self.stops.push(stop);
			}
			stop.commitAll();
			$.post("/stop/save", { "id" : stop.id(), "title" : stop.title(), "agencyTag" : stop.agencyChoice().tag,	"lineTag" : stop.lineChoice().tag, "directionTag" : stop.directionChoice().tag,	"stopTag" : stop.stopChoice().tag, "timeToStop" : stop.timeToStop() }, function(data) {
				if (data) {
					stop.id(parseInt(data.id));
					stop.lat(parseFloat(data.lat));
					stop.lon(parseFloat(data.lon));
					self.loadPredictions();
					self.loadLines();
				}
				else {
					alert("Problem updating data on server. Please submit again.");
					self.editingStop(stop);
				}
			}, 'json');
			self.editingStop().directions([]);
			self.editingStop(false);
		}
		else {
			alert("Please select an agency, line, direction, and stop.");
		}
	};
	
	this.deleteStop = function(i) {
		if (confirm("Do you really want to delete this stop?")) {
			$.post("/stop/delete", { "id" : self.stops()[i].id() }, function(data) {
				if (!data || !(data.id)) {
					alert("Problem updating data on server.");
				}
				self.loadLines();
			}, 'json');
			self.stops()[i].undraw();
			self.stops.splice(i, 1);
			layoutFooter();
		}
	};
	
	// settings
	this.loadingSettings = ko.observable(true);
	this.maxArrivals = ko.protectedObservable(3);
	this.showMissed = ko.protectedObservable(true);
	this.mapType = ko.protectedObservable("roadmap");
	this.showControls = ko.protectedObservable("yes");
	
	this.editingSettings = ko.observable(false);
	
	this.editSettings = function() {
		if (self.loadingSettings()) {
			alert("Settings data still loading. Please wait");
		}
		else {
			self.editingSettings(true);
		}
	};
	
	this.cancelEditingSettings = function() {
		self.maxArrivals.reset();
		self.showMissed.reset();
		self.mapType.reset();
		self.showControls.reset();
		self.editingSettings(false);
	};
	
	this.doneEditingSettings = function() {
		self.maxArrivals.commit();
		self.showMissed.commit();
		self.mapType.commit();
		self.showControls.commit();
		$.post("/settings", { "maxArrivals": self.maxArrivals(), "showMissed": self.showMissed(), 'mapType' : self.mapType(), 'showControls' : self.showControls() }, function(data) {
				if (!data || !data.saved) {
					alert("Problem updating data on server. Please submit again.");
					self.editingSettings(true);
				}
				else {
					self.loadPredictions();
				}
			}, 'json');
		setMapType(self.mapType());
		setShowControls(self.showControls());
		self.editingSettings(false);
	};
	
	this.loadSettings = function() {
		self.loadingSettings(true);
		$.get("/settings", function(settings) {
			self.maxArrivals(settings.maxArrivals);
			self.showMissed(settings.showMissed);
			self.mapType(settings.mapType);
			self.showControls(settings.showControls);
			self.maxArrivals.commit();
			self.showMissed.commit();
			self.mapType.commit();
			self.showControls.commit();
			self.loadingSettings(false);
		}, 'json');
	};
	
	// feedback form
	
	this.editingFeedback = ko.observable(false);
	this.feedbackText = ko.observable("");
	
	this.showFeedbackForm = function() {
		self.editingFeedback(true);
	};
	
	this.cancelEditingFeedback = function() {
		self.editingFeedback(false);
	};
	
	this.submitFeedback = function() {
		$.post("/feedback", { "feedback": self.feedbackText() }, function(data) {
			if (!data || !data.sent) {
				alert("Problem sending your feedback. Please submit again.");
			}
			else {
				alert("Feedback sent! Thank you!");
				self.feedbackText("");
				self.editingFeedback(false);
			}
		}, 'json');
	};
	
	// loading the stops
	
	this.isLoadingStops = ko.observable(true);
	
	this.loadStops = function() {
		self.isLoadingStops(true);
		$.get("/stops", function(stops) {
			var mappedStops = $.map(stops, function(aStop, index) {
				return new stop(aStop);
			});
			self.stops(mappedStops);
			self.isLoadingStops(false);
			layoutFooter();
			self.refreshTimer();
		}, 'json');
	};
	
	// loading the lines
	
	this.isLoadingLines = ko.observable(true);
	
	this.loadLines = function() {
		self.isLoadingLines(true);
		$.get("/lines", function(lines) {
			var mappedLines = $.map(lines, function(aLine, index) {
				var theLine = self.lineFromTags(aLine.agencyTag, aLine.lineTag);
				if (theLine) {
					return theLine;
				}
				return new line(aLine);
			});
			for (var i=0; i < self.lines().length;i++) {
				var found = false;
				var theLine = self.lines()[i];
				for (var j=0; j < mappedLines.length;j++) {
					var aLine = mappedLines[j];
					if (theLine.agencyTag == aLine.agencyTag && theLine.lineTag == aLine.lineTag) {
						found = true;
						break;
					}
				}
				if (!found) {
					theLine.undraw();
				}
			}
			self.lines(mappedLines);
			self.isLoadingLines(false);
			self.loadVehicles();
		}, 'json');	
	};
	
	// loading the predictions
	this.isLoadingPredictions = ko.observable(true); // use this in the ui
	
	this.loadPredictions = function() {
		self.isLoadingPredictions(true);
		$.get("/predictions", function(predictions) {
			$.map(predictions, function(aPrediction, i) {
				var theStop = self.stopWithId(aPrediction.id);
				var mappedDirections = $.map(aPrediction.directions, function(aDirection) {
//					for (var i=0; i < theStop.directions().length; i++) {
//						if (theStop.directions()[i].title() == aDirection.title) {
//							var theDirection = theStop.directions()[i];
//							theDirection.updateDestinations(aDirection.destinations);
//							return theDirection;
//						}
//					}
					return new direction(theStop, aDirection.title, aDirection.destinations);
				});
				theStop.directions(mappedDirections);
				self.isLoadingPredictions(false);
				layoutFooter();
			});
		}, 'json');
	};
	
	// loading the vehicles
	
	this.isLoadingVehicles = ko.observable(true);
	
	this.lineFromTags = function(agencyTag, lineTag) {
		var lineToReturn = null;
		self.lines().forEach(function(aLine, i) {
			if (aLine.agencyTag == agencyTag && aLine.lineTag == lineTag) {
				lineToReturn = aLine;
			}
		});
		return lineToReturn;
	};
	
	this.loadVehicles = function() {
		self.isLoadingVehicles(true);
		$.get("/vehicles/0", function(lines) {
			lines.forEach(function(aLine, i) {
				var theLine = self.lineFromTags(aLine.agencyTag, aLine.lineTag);
				var mappedVehicles = $.map(aLine.vehicles, function(aVehicle, index) {
					var theVehicle = theLine.vehicleFromId(aVehicle.id);
					if (theVehicle) {
						theVehicle.lat(aVehicle.lat);
						theVehicle.lon(aVehicle.lon);
						theVehicle.heading(aVehicle.heading);
						theVehicle.directionTag(aVehicle.directionTag);
						return theVehicle;
					}
					return new vehicle(aVehicle, theLine);
				});
				for (var i=0; i < theLine.vehicles().length; i++) {
					var found = false;
					for (var j=0; j < aLine.vehicles.length; j++) {
						if (theLine.vehicles()[i].id == aLine.vehicles[j].id) {
							found = true;
							break;
						}
					}
					if (!found) {
						theLine.vehicles()[i].undraw();
					}
				}
				theLine.vehicles(mappedVehicles);
				self.isLoadingVehicles(false);
			});
		}, 'json');
	};
	
	// refresh timer
	
	this.refreshTimer = function() {
		if (navigator.onLine) {
			self.showOfflineWarning(false);
			if (!self.isLoadingStops() && !self.isLoadingLines()) {
				self.loadPredictions();
				self.loadVehicles();
				setTimeout(self.refreshTimer, 20000);
			}
			else {
				setTimeout(self.refreshTimer, 1000);
			}
		}
		else {
			self.showOfflineWarning(true);
			setTimeout(self.refreshTimer, 10000);
		}
	};
	
	// offline dialog
	
	this.showOfflineWarning = ko.observable(false);
};

/* MAP / LAYOUT HELPERS */

function initialize() {

	window.onresize = layoutFooter;

	var myOptions = {
		disableDefaultUI: true,
	};
	map = new google.maps.Map(document.getElementById('map'), myOptions);
	
	$.get("/map", function(data) {
		map.setZoom(data.zoom);
		map.setCenter(new google.maps.LatLng(data.lat, data.lon));
		setMapType(data.mapType);
		setShowControls(data.showControls);
				
		google.maps.event.addListener(map, 'center_changed', function() {
			clearTimeout(saveMapDefaultsTimer);
			saveMapDefaultsTimer = window.setTimeout(saveMapDefaults, 2000);
		});
		
		google.maps.event.addListener(map, 'zoom_changed', function() {
			clearTimeout(saveMapDefaultsTimer);
			saveMapDefaultsTimer = window.setTimeout(saveMapDefaults, 2000);
		});
		
		plotUserLocation();
		layoutFooter();
		
		vm = new viewModel();
		ko.applyBindings(vm);
		vm.loadStops();
		vm.loadLines();
		vm.loadSettings();
		
	}, 'json');
}

function layoutFooter() {
	var windowHeight = $(window).height();
	var wrapperHeight = document.getElementById("wrapper").scrollHeight;
	if (wrapperHeight <= windowHeight) {
		$("#footer").css("position", "absolute");
		$("#footer").css("bottom", "0");
	}
	else if (wrapperHeight > windowHeight) {
		$("#footer").css("position", "relative");
	}
}

function setShowControls(showControls) {
	if (showControls == "yes") {
		var myOptions = {
			disableDefaultUI: true,
			
			panControl: true,
			panControlOptions: {
				position: google.maps.ControlPosition.TOP_RIGHT
			},
			
			zoomControl: true,
			zoomControlOptions: {
				style: google.maps.ZoomControlStyle.LARGE,
				position: google.maps.ControlPosition.TOP_RIGHT
			},
		};
	}
	else {
		var myOptions = {
			disableDefaultUI: true,
			panControl: false,
			zoomControl: false,
		};
	}
	map.setOptions(myOptions);
}

function setMapType(mapType) {
	if (mapType == "roadmap") {
		map.setMapTypeId(google.maps.MapTypeId.ROADMAP);
	}
	else {
		map.setMapTypeId(google.maps.MapTypeId.SATELLITE);
	}
}

function saveMapDefaults() {
	$.post("/map", { "zoom": map.getZoom(), "lat": map.getCenter().lat(), "lon": map.getCenter().lng() });
}

function plotUserLocation() {
	if (navigator.geolocation) { // check if browser support this feature or not 
		navigator.geolocation.getCurrentPosition(function(position) {
			var lat = position.coords.latitude;
			var lng = position.coords.longitude;
			
			var locationCircle = new google.maps.Circle({
				strokeColor: "#FFAD29",
				strokeOpacity: 0.8,
				strokeWeight: 2,
				fillColor: "#000000",
				fillOpacity: 0.2,
				map: map,
				center: new google.maps.LatLng(lat, lng),
				radius: 300
			});
			
			var image = new google.maps.MarkerImage('/images/user-location.png',
				null, // size
				new google.maps.Point(0,0), // origin
				new google.maps.Point(15, 23) // anchor
			);
			
			var locationPoint = new google.maps.Marker({
				position: new google.maps.LatLng(lat, lng),
				map: map,
				icon: image
			});
		});
	}
}

/* MAIN */

if ((navigator.userAgent.match(/iPhone/i)) || (navigator.userAgent.match(/iPod/i))  || ((navigator.userAgent.match(/Android/i)) && (navigator.userAgent.match(/mobile/i)))) {
    isMobile = true;
}
else {
    isMobile = false;
}

google.maps.event.addDomListener(window, 'load', initialize);