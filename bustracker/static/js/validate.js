function validate() {
	var title = $('#title').val();
	var agency = $('#agency-select').val();
	var nextbusLine = $('#nextbus-line-select').val();
	var nextbusDirection = $('#nextbus-stop-select').val();
	var nextbusStop = $('#nextbus-stop-select').val();
	var bartStation = $('#bart-station-select').val();
	var bartDirection = $('#bart-direction-select').val();	
	var timeToStop = $('#time-to-stop').val();
	
	if (!title) {
		alert("You must enter a title for your stop.");
		return false;
	}
	else if (!agency) {
		alert("You must select a transit agency and then a stop.");
		return false;
	}
	else if (agency == "bart" && (!bartStation || !bartDirection)) {
		alert("You must select a station and a direction.");
		return false;
	}
	else if (agency != "bart" && (!nextbusLine || !nextbusDirection || !nextbusStop)) {
		alert("You must select a line, direction, and stop.");
		return false;
	}
	else if (!timeToStop || parseInt(timeToStop) != timeToStop) {
		alert("Time to stop must be a whole positive number.");
		return false;
	}
	else {
		return true;
	}
}