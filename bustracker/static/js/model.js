var stop = function(aStop)
{
	var self = this;

	if (aStop != null) {
		this.id = ko.observable(aStop.id);
		this.title = ko.observable(aStop.title);
		
		this.timeToStop = ko.observable(aStop.timeToStop);
		this.directions = ko.observableArray([]);
		this.position = ko.observable(aStop.position);
	}
	else {
		this.id = ko.observable();
		this.title = ko.observable("untitled stop");
		
		this.timeToStop = ko.observable(0);
		this.directions = ko.observableArray([]);
		this.position = ko.observable(0);
	}
	
	this.agencyChoices = ko.observableArray([]);
	this.lineChoices = ko.observableArray([]);
	this.directionChoices = ko.observableArray([]);
	this.stopChoices = ko.observableArray([]);
	
	this.agencyChoice = ko.observable(null);
	this.lineChoice = ko.observable(null);
	this.directionChoice = ko.observable(null);
	this.stopChoice = ko.observable(null);
	
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
	var self = this;
	
	this.destination = ko.observable(destination);
	this.minutes = ko.observable(minutes);
	
	this.timeToLeave = ko.dependentObservable(function() {
		return minutes - timeToStop();
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
	
	this.isLoading = ko.observable(false);
	this.stops = ko.observableArray([]);
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
		var newStop = new stop(null);
		self.stops.push(newStop);
		self.editingStop(newStop);
	}
	
	this.editStop = function(i) {
		self.editingStop(self.stops()[i]);
	}
	
	this.doneEditingStop = function() {
		stop = self.editingStop();
		if (stop.agencyChoice() && stop.lineChoice() && stop.directionChoice() && stop.stopChoice()) {
			$.post("/stop/save", { "id" : stop.id(), "title" : stop.title(), "agencyTag" : stop.agencyChoice().tag,	"lineTag" : stop.lineChoice().tag, "directionTag" : stop.directionChoice().tag,	"stopTag" : stop.stopChoice().tag, "timeToStop" : stop.timeToStop() }, function(data) {
				if (data) {
					stop.id(parseInt(data.id));
					self.refresh();
				}
				else {
					alert("Problem updating data on server. Please submit again.");
					self.editingStop(stop);
				}
			}, 'json');
			self.editingStop().directions([])
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
			}, 'json');
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
			self.refreshTimer();
		}, 'json');	
	}
	
	this.refreshTimer = function() {
		self.refresh();
		setTimeout(self.refreshTimer, 20000);
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
	}
};