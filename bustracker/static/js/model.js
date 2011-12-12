var colorList = function() {
	var self = this;
	this.i = 0;
	this.colors = ["#FFAD29", "#5CE1FF", "#A89CFF", "#FF4FA7", "#FFF129", "#45FF70", "#C23C3C"];
	this.color = function() {
		self.i++;
		return self.colors[self.i % self.colors.length];
	}
}

var aColorList = new colorList();

var line = function(aLine) {

	var self = this;
	this.agencyTag = aLine.agencyTag;
	this.lineTag = aLine.lineTag;
	this.color = aColorList.color();
	this.polyLineList = [];
	
	this.undraw = function() {
		for (var i=0; i < self.polyLineList.length;i++) {
			self.polyLineList[i].setMap(null);
		}
	}

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
	}
	
	this.draw();
}

var userLocation = function() {

    this.locationCircle = new google.maps.Circle({
		strokeColor: "#FFAD29",
		strokeOpacity: 0.8,
		strokeWeight: 2,
		fillColor: "#000000",
		fillOpacity: 0.2,
		map: map,
		center: new google.maps.LatLng(self.lat(), self.lon()),
		radius: 200
    });

}

var stop = function(aStop)
{
	var self = this;

	if (aStop != null) {
		this.id = ko.observable(aStop.id);
		this.title = ko.observable(aStop.title);
		this.lat = ko.observable(aStop.lat);
		this.lon = ko.observable(aStop.lon);
		this.timeToStop = ko.observable(aStop.timeToStop);
	}
	else {
		this.id = ko.observable();
		this.title = ko.observable("untitled stop");
		this.lat = ko.observable(0);
		this.lon = ko.observable(0);
		this.timeToStop = ko.observable(0);
	}
	
	this.marker = new google.maps.Marker({
		position: new google.maps.LatLng(self.lat(), self.lon()),
		map: map,
		icon: '/images/stop.png'
	});
	
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
	
	// choice updating functions
	this.updateAgencyChoices = ko.dependentObservable(function() {
		$.get("/agencies", function(agencies) {
			var mappedAgencyChoices = $.map(agencies, function(anAgency, index) {
				return new selectionChoice(anAgency.title, anAgency.tag);
			});
			self.agencyChoices(mappedAgencyChoices);
			if (aStop.agencyTag) {
				self.agencyChoice(self.choiceFromTag(aStop.agencyTag, mappedAgencyChoices));
				aStop.agencyTag = null;
			}
		}, 'json');
		return "";
	}, this);
	
	this.updateLineChoices = ko.dependentObservable(function() {
		if (self.agencyChoice()) {
			$.get("/" + self.agencyChoice().tag + "/lines", function(lineChoices) {
				var mappedLineChoices = $.map(lineChoices, function(aLineChoice, index) {
					return new selectionChoice(aLineChoice.title, aLineChoice.tag);
				});
				self.lineChoices(mappedLineChoices);
				if (aStop.lineTag) {
					self.lineChoice(self.choiceFromTag(aStop.lineTag, mappedLineChoices));
					aStop.lineTag = null;
				}
			}, 'json');
		}
		else {
			self.lineChoice(null);
			self.lineChoices([]);
		}
		return "";
	}, this);
	
	this.updateDirectionChoices = ko.dependentObservable(function() {
		if (self.agencyChoice() && self.lineChoice()) {
			$.get("/" + self.agencyChoice().tag + "/" + self.lineChoice().tag + "/directions", function(directionChoices) {
				var mappedDirectionChoices = $.map(directionChoices, function(aDirectionChoice, index) {
					return new selectionChoice(aDirectionChoice.title, aDirectionChoice.tag);
				});
				self.directionChoices(mappedDirectionChoices);
				if (aStop.directionTag) {
					self.directionChoice(self.choiceFromTag(aStop.directionTag, mappedDirectionChoices));
					aStop.direcitonTag = null;
				}
			}, 'json');
		}
		else {
			self.directionChoice(null);
			self.directionChoices([]);
		}
		return "";
	}, this);
	
	this.updateStopChoices = ko.dependentObservable(function() {
		if (self.agencyChoice() && self.lineChoice()  && self.directionChoice()) {
			$.get("/" + self.agencyChoice().tag + "/" + self.lineChoice().tag + "/" + self.directionChoice().tag + "/stops", function(stopChoices) {
				var mappedStopChoices = $.map(stopChoices, function(aStopChoice, index) {
					return new selectionChoice(aStopChoice.title, aStopChoice.tag);
				});
				self.stopChoices(mappedStopChoices);
				if (aStop.stopTag) {
					self.stopChoice(self.choiceFromTag(aStop.stopTag, mappedStopChoices));
					aStop.stopTag = null;
				}
			}, 'json');
		}
		else {
			self.stopChoice(null);
			self.stopChoices([]);
		}
		return "";
	}, this);
}

var direction = function(stop, title, destinations)
{
	var self = this;
	this.title = ko.observable(title);
	this.destinations = ko.observableArray([]);
	
	this.updateDestinations = function(destinations) {
		var mappedDestinations = $.map(destinations, function(aDestination) {
			for (var i=0; i < self.destinations().length; i++) {
				if (self.destinations()[i].title() == aDestination.title) { // convert this to a dependant observable?
					var theDestination = self.destinations()[i];
					theDestination.updateVehicles(aDestination.vehicles);
					return theDestination;
				}
			}
			return new destination(stop, aDestination.title, aDestination.vehicles);
		});
		self.destinations(mappedDestinations);
	}
	this.updateDestinations(destinations);
}

var destination = function(stop, title, vehicles)
{
	var self = this;
	
	this.direction = ko.observable(direction);
	this.title = ko.observable(title);
	this.vehicles = ko.observableArray([]);
	
	this.updateVehicles = function(vehicles) {
		var mappedVehicles = $.map(vehicles, function(aVehicle) {
			for (var i=0; i < self.vehicles().length; i++) {
				if (self.vehicles()[i].vehicleNumber == aVehicle.number) { // convert this to a dependant observable?
					var theVehicle = self.vehicles()[i];
					theVehicle.minutes(aVehicle.minutes);
					theVehicle.lat(aVehicle.lat);
					theVehicle.lon(aVehicle.lon);
					return theVehicle;
				}
			}
			return new vehicle(stop, aVehicle.minutes, aVehicle.lat, aVehicle.lon, aVehicle.number);
		});
		for (var i=0; i < self.vehicles().length; i++) {
			var found = false;
			for (var j=0; j < self.mappedVehicles.length; j++) {
				if (self.mappedVehicles[j] == self.vehicles()[i]) {
					found = true;
				}
				if (!found) {
					self.vehicles()[i].removeMarker();
				}
			}
		}
		self.vehicles(mappedVehicles);
	}
	
	this.updateVehicles(vehicles);
}

var vehicle = function(stop, minutes, lat, lon, vehicleNumber)
{
	var self = this;
	
	this.vehicleNumber = vehicleNumber;
	this.minutes = ko.observable(minutes);
	this.lat = ko.observable(lat);
	this.lon = ko.observable(lon);
	this.marker = null;
	
	this.lat.subscribe(function(newValue) {
		self.updateVehicleMarker();
	});
	this.lon.subscribe(function(newValue) {
		self.updateVehicleMarker();
	});
	
	this.moveToStep = function(marker, startPoint, stepCurrent, stepsTotal) {
		if (stepCurrent < stepsTotal) {
			marker.setPosition(new google.maps.LatLng(parseFloat(startPoint.lat() + stepCurrent*((self.lat() - startPoint.lat()) / stepsTotal)), parseFloat(startPoint.lng() + stepCurrent*((self.lon() - startPoint.lng())/ stepsTotal))));
			window.setTimeout(function() {
				self.moveToStep(marker, startPoint, stepCurrent+1, stepsTotal);
			}, 100);
		}
	}
	
	this.removeMarker = function() {
		if (self.marker) {
			self.marker.setMap(null);
			self.marker = null;
		}
	}
	
	this.updateVehicleMarker = function() {
		if (self.marker) {
			//distance = google.maps.geometry.spherical.computeDistanceBetween(latLngA, latLngB);
			self.moveToStep(self.marker, self.marker.position, 0, 20);
		}
		else if (self.lat() != 0 && self.lon() != 0) {
			self.marker = new google.maps.Marker({
				position: new google.maps.LatLng(self.lat(), self.lon()),
				map: map,
				icon: 'https://chart.googleapis.com/chart?chst=d_bubble_icon_text_small&chld=bus|bb|' + stop.title() + ' (' + self.minutes().toString() + 'm)|FFFFFF|000000'//google.maps.MarkerImage('https://chart.googleapis.com/chart?chst=d_bubble_icon_text_small&chld=bus|bb|51A (' + self.minutes().toString() + 'm)|FFFFFF|000000', null, new google.maps.Point(0, 42))
			});
		}
	}
	this.updateVehicleMarker();
	
	this.timeToLeave = ko.dependentObservable(function() {
		return minutes - stop.timeToStop();
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
		if (self.minutes() > 0) {
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
		else if (self.timeToLeave() == 1) {
			return "leave in 1m";
		}
		else {
			return "leave in " + self.timeToLeave().toString() + "m";
		}
		
	}, this);
}

var selectionChoice = function(title, tag) {
	this.title = title;
	this.tag = tag;
}

/* View Model */

var viewModel = function() {
	var self = this;
	
	this.isLoadingStops = ko.observable(false);
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
	
	// stop actions
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
	
	this.newStop = function() {
		self.isNewStop = true;
		self.editingStop(new stop(null));
	}
	
	this.editStop = function(i) {
		self.isNewStop = false;
		self.editingStop(self.stops()[i]);
	}
	
	this.cancelEditingStop = function() {
		self.editingStop(false);
	}
	
	this.doneEditingStop = function() {
		stop = self.editingStop();
		if (stop.agencyChoice() && stop.lineChoice() && stop.directionChoice() && stop.stopChoice()) {
			if (self.isNewStop) {
				self.stops.push(stop);
			}
			adjustLayout();
			$.post("/stop/save", { "id" : stop.id(), "title" : stop.title(), "agencyTag" : stop.agencyChoice().tag,	"lineTag" : stop.lineChoice().tag, "directionTag" : stop.directionChoice().tag,	"stopTag" : stop.stopChoice().tag, "timeToStop" : stop.timeToStop() }, function(data) {
				if (data) {
					stop.id(parseInt(data.id));
					self.refresh();
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
	}
	
	this.delete = function(i) {
		if (confirm("Do you really want to delete this stop?")) {
			$.post("/stop/delete", { "id" : self.stops()[i].id() }, function(data) {
				if (!data || !(data.id)) {
					alert("Problem updating data on server.");
				}
				self.loadLines();
			}, 'json');
			self.stops.splice(i, 1);
			adjustLayout();
		}
	}
	
	// loading the stops
	this.loadStops = function() {
		self.isLoadingStops(true);
		$.get("/stops", function(stops) {
			var mappedStops = $.map(stops, function(aStop, index) {
				return new stop(aStop);
			});
			self.stops(mappedStops);
			self.isLoadingStops(false);
			self.refreshTimer();
			adjustLayout();
		}, 'json');	
	}
	
	// updating the predictions
	this.refreshTimer = function() {
		self.refresh();
		setTimeout(self.refreshTimer, 20000);
	}
	
	this.refresh = function() {
		$.get("/predictions", function(predictions) {
			$.map(predictions, function(aPrediction, i) {
				var theStop = self.stopWithId(aPrediction.id);
				var mappedDirections = $.map(aPrediction.directions, function(aDirection) {
					for (var i=0; i < theStop.directions().length; i++) {
						if (theStop.directions()[i].title() == aDirection.title) {
							var theDirection = theStop.directions()[i];
							theDirection.updateDestinations(aDirection.destinations);
							return theDirection;
						}
					}
					return new direction(theStop, aDirection.title, aDirection.destinations);
				});
				theStop.directions(mappedDirections);
				adjustLayout();
			});
		}, 'json');
	}
	
	// loading the lines
	this.loadLines = function() {
		$.get("/lines", function(lines) {
			for (var i=0; i < self.lines().length;i++) {
				self.lines()[i].undraw();
			}
		
			var mappedLines = $.map(lines, function(aLine, index) {
				return new line(aLine);
			});
			self.lines(mappedLines);
		}, 'json');	
	}
};