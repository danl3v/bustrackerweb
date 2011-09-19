from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.api import mail
from models import models
import view

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
            view.renderTemplate(self, 'predictions.html', { 'show_news_feed' : user.show_news_feed })
        else:
            view.renderTemplate(self, 'index.html', {})

class Feedback(webapp.RequestHandler):
    def get(self):
        '''Render the home page.'''
        view.renderTemplate(self, 'feedback.html', {})
    def post(self):
        current_user = users.get_current_user()
        mail.send_mail(
              sender=current_user.email(),
              to="dlouislevy@gmail.com",
              subject="trackmyb.us feedback",
              body=self.request.get("feedback")
        )
    
        view.renderTemplate(self, 'feedback_success.html', {})

class Settings(webapp.RequestHandler):
    def get(self):
        '''Render the settings page.'''
        current_user = users.get_current_user()
        user = models.User.all().filter('user =', current_user).get()
        view.renderTemplate(self, 'settings.html', { 'max_arrivals': user.max_arrivals, 'show_missed': user.show_missed, 'show_news_feed' : user.show_news_feed, 'time_zone_offset' : user.time_zone_offset })
    def post(self):
        current_user = users.get_current_user()
        user = models.User.all().filter('user =', current_user).get()
        if user:
            user.max_arrivals = int(self.request.get("max-arrivals"))
            user.show_missed = True if self.request.get("show-missed") == "yes" else False
            user.show_news_feed = int(self.request.get("show-news-feed"))
            user.time_zone_offset = int(self.request.get("time-zone-offset"))
            user.put()
        self.redirect("/")