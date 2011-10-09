/* 
 * stop_selector.js
 * TrackMyBus
 */

$(document).ready(function() {
	
	$('#nextbus-menus').hide();
	$('#bart-menus').hide();

	$('#agency-select').change(function() {
		if ($('#agency-select').val() == "bart") {
			$('#nextbus-menus').hide();
			$('#bart-menus').show();
			bartSetStation(null);
		}
		else {
			$('#bart-menus').hide();
			$('#nextbus-menus').show();
			nextbusSetLine($('#agency-select').val(), null);
		}
	});
	
	$('#bart-station-select').change(function() {
		bartSetDirection(null);
	});
	
	$('#nextbus-line-select').change(function() {
		nextbusSetDirection($('#agency-select').val(), $('#nextbus-line-select').val(), null);
	});
	
	$('#nextbus-direction-select').change(function() {
		nextbusSetStop($('#agency-select').val(), $('#nextbus-line-select').val(), $('#nextbus-direction-select').val(), null);
	});
});

function bartSetStation(station) {
	$('#bart-direction-select').html('');
	$.post('/bart/stations', { 'station' : station }, function(data) {
		$('#bart-station-select').html(data);
	});
}

function bartSetDirection(direction) {
	$.post('/bart/directions', { 'direction' : direction }, function(data) {
		$('#bart-direction-select').html(data);
	});
}

function nextbusSetLine(agency, line) {
	$('#nextbus-line-select').html('<option value="">Loading...</option>');
	$('#nextbus-direction-select').html('');
	$('#nextbus-stop-select').html('');
	$.post('/nextbus/lines', { 'agency' : agency, 'line' : line }, function(data) {
		$('#nextbus-line-select').html(data);
	});
}

function nextbusSetDirection(agency, line, direction) {
	$('#nextbus-direction-select').html('<option value="">Loading...</option>');
	$('#nextbus-stop-select').html('');
	$.post('/nextbus/directions', { 'agency' : agency, 'line' : line, 'direction' : direction }, function(data) {
		$('#nextbus-direction-select').html(data);
	});
}

function nextbusSetStop(agency, line, direction, stop) {
	$('#nextbus-stop-select').html('<option value="">Loading...</option>');
	$.post('/nextbus/stops', { 'agency' : agency, 'line' : line, 'direction' : direction, 'stop' : stop }, function(data) {
		$('#nextbus-stop-select').html(data);
	});
}