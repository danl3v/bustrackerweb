var stop = function(aStop)
{
	var self = this;
	
	if (aStop != null) {
		this.id = ko.observable(aStop.id);
		this.title = ko.observable(aStop.title);
		
		this.agencyChoice = ko.observable(vm.agencyFromTag(aStop.agencyTag));
		this.lineChoice = ko.observable(vm.lineFromTag(aStop.lineTag));
		
		this.agencyTag = ko.observable(aStop.agencyTag); // phase these out in favor of above things
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
	
	this.lineFromTag = function(tag) {
		var theChoice = null;
		self.lineChoices.forEach(function(aLineChoice, i) {
			if (aLineChoice.tag == tag) {
				theChoice = aLineChoice;
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
		var newStop = new stop(null);
		self.stops.push(newStop);
		self.editingStop(newStop);
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
	this.agencyChoices = ko.observableArray([]);
	this.lineChoices = ko.observableArray([]);
	this.directionChoices = ko.observableArray([]);
	
	this.updateAgencyChoices = ko.dependentObservable(function() {
		$.get("/agencies", function(agencies) {
			var mappedAgencies = $.map(agencies, function(anAgency, index) {
				return new selectionChoice(anAgency.title, anAgency.tag);
			});
			self.agencyChoices = mappedAgencies;
		}, 'json');
		return "";
	}, this);
	
	this.updateLineChoices = ko.dependentObservable(function() {
		if (self.editingStop() && self.editingStop().agencyChoice()) {
			$.get("/" + self.editingStop().agencyChoice().tag + "/lines", function(lineChoices) {
				var mappedLineChoices = $.map(lineChoices, function(aLineChoice, index) {
					return new selectionChoice(aLineChoice.title, aLineChoice.tag);
				});
				self.lineChoices(mappedLineChoices);
			}, 'json');
		}
		return "";
	}, this);
	
	this.updateDirectionChoices = ko.dependentObservable(function() {
		if (self.editingStop()) {
							alert("going");
			if (self.editingStop().agencyChoice() && self.editingStop().lineChoice()) {

				$.get("/" + self.editingStop().agencyChoice().tag + "/" + self.editingStop().lineChoice().tag + "/directions", function(directionChoices) {
					alert(directionChoices);
				});
			}
		}
		return "";
	}, this);
	
	
	
	
};