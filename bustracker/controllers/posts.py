from google.appengine.ext import webapp
from google.appengine.api import users
from models import models
import view

class Posts(webapp.RequestHandler):
    def get(self):
        current_user = users.get_current_user()
        posts = models.User.all().filter('user =', current_user).get().posts.order('-created')
        if posts.count() == 0:
            self.response.out.write('<tr class="header1" colspan="2"><td class="header1-left">You have no posts. <a href="/post/new">Add one</a>.</td></tr>')
        else:
            self.response.out.write('<tr class="header1"><td class="header1-left">News Feed</td><td class="header1-right"><a href="/post/new">new post</a></td></tr>')
            for post in posts:
                self.response.out.write('<tr class="header4"><td colspan="2"><span class="body">' + post.body + '</span>')
                self.response.out.write('<span class="details">' + post.pretty_created + '<span class="tools"> <span class="separator">|</span> <a href="/post/edit/' + str(post.key().id()) + '">edit</a> <span class="separator">|</span> <a href="/post/delete/' + str(post.key().id()) + '">delete</a></span></span></td></tr>')

class NewPost(webapp.RequestHandler):
    def get(self):
        '''Load the new post page.'''
        view.renderTemplate(self, 'new_post.html', {})
    def post(self):
        '''Add a new post for a user.'''
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