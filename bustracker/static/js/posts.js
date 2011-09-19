function getPosts() {
	$.get('/posts', function(posts) {
		$('#news-feed-list').html(posts);
	});
	setTimeout("getPosts()", 60000);
}

$(document).ready(function() {
	getPosts();
});