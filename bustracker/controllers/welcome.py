from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.api import mail
from models import models
import view
from django.utils import simplejson as json

class MainPage(webapp.RequestHandler):
    def get(self):
        '''Render the home page.'''
        current_user = users.get_current_user()
        if current_user:
            user = models.User.all().filter('user =', current_user).get()
            if not user:
                user = models.User()
                user.user = current_user
                user.put()
            view.renderTemplate(self, 'predictions.html', {
                'show_news_feed' : user.show_news_feed,
                'news_feed_width' : user.news_feed_width,
                'show_banner': user.show_banner
            })
        else:
            view.renderTemplate(self, 'index.html', {})

class Feedback(webapp.RequestHandler):
    def post(self):
        current_user = users.get_current_user()
        mail.send_mail(
              sender=current_user.email(),
              to="dlouislevy@gmail.com",
              subject="trackmyb.us feedback",
              body=self.request.get("feedback")
        )
        self.response.out.write(json.dumps({ 'sent' : True }))

class Settings(webapp.RequestHandler):
    def get(self):
        '''Render the settings page.'''
        current_user = users.get_current_user()
        user = models.User.all().filter('user =', current_user).get()
        self.response.out.write(json.dumps({ 'maxArrivals' : user.max_arrivals, 'showMissed' : "yes" if user.show_missed else "no" }))
        
    def post(self):
        current_user = users.get_current_user()
        user = models.User.all().filter('user =', current_user).get()
        if user:
            user.max_arrivals = int(self.request.get("maxArrivals"))
            user.show_missed = True if self.request.get("showMissed") == "yes" else False
            user.put()
        self.response.out.write(json.dumps({ 'saved' : True }))