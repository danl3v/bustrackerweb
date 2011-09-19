function getPosts() {
	$.get('/posts', function(posts) {
		$('#news-feed-list').html(posts);
	});
	setTimeout("getPosts()", 20000);
}

$(document).ready(function() {
	getPosts();
});