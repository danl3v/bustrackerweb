function validate() {
	var agency = $('#agency-select').val();
	var line = $('#line-select').val();
	var direction = $('#stop-select').val();
	var stop = $('#stop-select').val();
	var timeToStop = $('#time-to-stop').val();
	if (!agency || !line || !direction || !stop) {
		alert("You must select a stop.");
		return false;
	}
	else if (parseInt(timeToStop) != timeToStop) {
		alert("Time to stop must be an integer.");
		return false;
	}
	return true;
}