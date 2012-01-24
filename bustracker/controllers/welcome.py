from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.api import mail
from models import models
import view
import default_user
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
        view.renderTemplate(self, 'index.html', { })

class Feedback(webapp.RequestHandler):
    def post(self):
        current_user = users.get_current_user()
        if current_user:
            sender_email = current_user.email()
        else:
            sender_email = "dlouislevy@gmail.com"
        mail.send_mail(
              sender=sender_email,
              to="dlouislevy@gmail.com",
              subject="trackmyb.us feedback",
              body=self.request.get("feedback")
        )
        self.response.out.write(json.dumps({ 'sent' : True }))

class Settings(webapp.RequestHandler):
    def get(self):
        '''Render the settings page.'''
        current_user = users.get_current_user()
        if current_user:
            user = models.User.all().filter('user =', current_user).get()
        else:
            user = default_user.user()
        self.response.out.write(json.dumps({ 'maxArrivals' : user.max_arrivals, 'showMissed' : "yes" if user.show_missed else "no", 'mapType' : user.map_type, 'showControls' : user.show_controls }))        
        
    def post(self):
        current_user = users.get_current_user()
        user = models.User.all().filter('user =', current_user).get()
        if user:
            user.max_arrivals = int(self.request.get("maxArrivals"))
            user.show_missed = True if self.request.get("showMissed") == "yes" else False
            user.map_type = self.request.get("mapType")
            user.show_controls = self.request.get("showControls")
            user.put()
        self.response.out.write(json.dumps({ 'saved' : True }))