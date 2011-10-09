from google.appengine.ext import webapp
from google.appengine.api import users
from models import models

import json, functions, view, time, datetime

class Posts(webapp.RequestHandler):
    def get(self):
        '''Return Posts or Tweets'''
        current_user = models.User.all().filter('user =', users.get_current_user()).get()
        show_news_feed = current_user.show_news_feed
        if (show_news_feed == "yes"):
            self.response.out.write(getPosts(current_user))
        elif (show_news_feed != "no"):
            self.response.out.write(getTweets(current_user))

class NewPost(webapp.RequestHandler):
    def get(self):
        '''Load the new post page.'''
        view.renderTemplate(self, 'new_post.html', {})
    def post(self):
        '''Add a new post for a user.'''
        body = self.request.get('body')
        if body:
            current_user = users.get_current_user()
            post = models.Post()
            post.user = models.User.all().filter('user =', current_user).get()
            post.body = self.request.get('body')
            post.put()
        self.redirect('/')
        
class EditPost(webapp.RequestHandler):
    def get(self, id):
        '''Load the edit post page.'''
        current_user = users.get_current_user()
        post = models.Post.get_by_id(int(id))
        if post and post.user.user == current_user:
            view.renderTemplate(self, 'edit_post.html', { 'post' : post })
        else:
            self.redirect('/')
    def post(self, id):
        '''Save changes to the post of a user.'''
        body = self.request.get('body')
        if body:
            current_user = users.get_current_user()
            post = models.Post.get_by_id(int(id))    
            if post and post.user.user == current_user:
                post.body = self.request.get('body')
                post.put()
        self.redirect('/')
        
class DeletePost(webapp.RequestHandler):
    def get(self, id):
        '''Delete a post.'''
        current_user = users.get_current_user()
        post = models.Post.get_by_id(int(id))
        if post and post.user.user == current_user:
            post.delete()
        self.redirect('/')
        
def getPosts(current_user):
    '''Return Posts.'''
    posts = current_user.posts.order('-created').fetch(limit=15)
    if len(posts) == 0:
        html = '<tr class="header1" colspan="2"><td class="header1-left">You have no posts. <a href="/post/new">Add one</a>.</td></tr>'
    else:
        html = '<tr class="header1"><td class="header1-left">News Feed</td><td class="header1-right"><a href="/post/new">new post</a></td></tr>'
        timezone = current_user.timezone
        for post in posts:
            html += '<tr class="header4"><td class="header4-post" colspan="2"><span class="body">' + post.body + '</span>'
            html += '<span class="details">' + functions.pretty_time(post.created, timezone) + '<span class="tools"> <span class="separator">|</span> <a href="/post/edit/' + str(post.key().id()) + '">edit</a> <span class="separator">|</span> <a href="/post/delete/' + str(post.key().id()) + '">delete</a></span></span></td></tr>'
    return html

def getTweets(current_user):
    '''Return Tweets.'''
    html = '<tr class="header1"><td class="header1-left" colspan="2">News Feed</td></tr>'
    theJSON = json.loads(functions.get_xml("http://search.twitter.com/search.json?q=from:" + current_user.show_news_feed + "&rpp=15&include_entities=true&with_twitter_user_id=true&result_type=recent"))
    timezone = current_user.timezone
    for result in theJSON['results']:
        created_at = datetime.datetime.fromtimestamp(time.mktime(time.strptime(result['created_at'], "%a, %d %b %Y %H:%M:%S +0000")))
        html += '<tr class="header4"><td class="header4-post" colspan="2"><span class="body">' + result['text'] + '</span>'
        html += '<span class="details">' + functions.pretty_time(created_at, timezone) + '</span></td></tr>'
    return html