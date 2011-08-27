function getPredictions() {
	$.get('/predictions', function(predictions) {
		$('#stop-list').html(predictions);
	});
	setTimeout("getPredictions()", 20000);
}

$(document).ready(function() {
	getPredictions();
});