$(document).ready(function() {
	$('#settings-news-feed').hide();
	$('#settings-twitter').hide();

	$('#show-news-feed').change(function() {
		if ($('#show-news-feed').val() == "no") {
			$('#settings-news-feed').fadeOut();
			$('#settings-twitter').fadeOut();
		}
		else if ($('#show-news-feed').val() == "yes") {
			$('#settings-news-feed').fadeIn();
			$('#settings-twitter').fadeOut();
		}
		else {
			$('#settings-news-feed').fadeIn();
			$('#settings-twitter').fadeIn();
		}
	});
	
	$('#show-news-feed').change();
});