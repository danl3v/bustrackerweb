/* 
 * settings.js
 * TrackMyBus
 */
 
$(document).ready(function() {
	if ($('#show-news-feed').val() == "no") {
			$('#settings-news-feed').hide();
			$('#settings-twitter').hide();
		}
		else if ($('#show-news-feed').val() == "yes") {
			$('#settings-news-feed').show();
			$('#settings-twitter').hide();
		}
		else {
			$('#settings-news-feed').show();
			$('#settings-twitter').show();
		}

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
});