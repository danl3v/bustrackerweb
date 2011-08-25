$(document).ready(function() {
	$('#agency-select').change(function() {
		setLine($('#agency-select').val(), null);
	});
	
	$('#line-select').change(function() {
		setDirection($('#agency-select').val(), $('#line-select').val(), null);
	});
	
	$('#direction-select').change(function() {
		setStop($('#agency-select').val(), $('#line-select').val(), $('#direction-select').val(), null);
	});
});

function setLine(agency, line) {
	$('#line-select').html('<option value="">Loading...</option>');
	$('#direction-select').html('');
	$('#stop-select').html('');
	$.post('/lines', { 'agency' : agency, 'line' : line }, function(data) {
		$('#line-select').html(data);
	});
}

function setDirection(agency, line, direction) {
	$('#direction-select').html('<option value="">Loading...</option>');
	$('#stop-select').html('');
	$.post('/directions', { 'agency' : agency, 'line' : line, 'direction' : direction }, function(data) {
		$('#direction-select').html(data);
	});
}

function setStop(agency, line, direction, stop) {
	$('#stop-select').html('<option value="">Loading...</option>');
	$.post('/stops', { 'agency' : agency, 'line' : line, 'direction' : direction, 'stop' : stop }, function(data) {
		$('#stop-select').html(data);
	});
}