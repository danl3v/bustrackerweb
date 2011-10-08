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
            view.renderTemplate(self, 'predictions.html', {
                'show_news_feed' : user.show_news_feed,
                'news_feed_width' : user.news_feed_width,
                'show_banner': user.show_banner
            })
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
        view.renderTemplate(self, 'settings.html', {
            'max_arrivals': user.max_arrivals,
            'show_missed': user.show_missed,
            'show_news_feed' : user.show_news_feed,
            'news_feed_width' : user.news_feed_width,
            'timezone' : user.timezone,
            'show_banner': user.show_banner
        })
    def post(self):
        current_user = users.get_current_user()
        user = models.User.all().filter('user =', current_user).get()
        if user:
            user.max_arrivals = int(self.request.get("max-arrivals"))
            user.show_missed = True if self.request.get("show-missed") == "yes" else False
            show_news_feed = self.request.get("show-news-feed")
            user.show_news_feed = show_news_feed if show_news_feed in ['yes', 'no'] else self.request.get('twitter-username')
            user.news_feed_width = int(self.request.get("news-feed-width"))
            user.timezone = self.request.get("timezone")
            user.show_banner = self.request.get("show-banner") if self.request.get("show-banner") != "" else None
            user.put()
        self.redirect("/")