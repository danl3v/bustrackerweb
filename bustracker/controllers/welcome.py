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
        view.renderTemplate(self, 'settings.html', { 'max_arrivals': user.max_arrivals, 'show_missed': user.show_missed, 'show_news_feed' : user.show_news_feed })
    def post(self):
        current_user = users.get_current_user()
        user = models.User.all().filter('user =', current_user).get()
        if user:
            user.max_arrivals = int(self.request.get("max-arrivals"))
            user.show_missed = True if self.request.get("show-missed") == "yes" else False
            user.show_news_feed = True if self.request.get("show-news-feed") == "yes" else False
            user.put()
        self.redirect("/")

class NewStop(webapp.RequestHandler):
    def get(self):
        '''Load the new stop page.'''
        view.renderTemplate(self, 'new_stop.html', {})
    
    def post(self):
        '''Add a new stop for a user.'''
        current_user = users.get_current_user()
        stop = models.Stop()
        stop.user = models.User.all().filter('user =', current_user).get()
        stop.title = self.request.get('title')
        stop.agency_tag = self.request.get('agency-select')
        if stop.agency_tag == "bart":
            stop.direction_tag = self.request.get('bart-direction-select')
            stop.stop_tag = self.request.get('bart-station-select')
        else:
            stop.line_tag = self.request.get('nextbus-line-select')
            stop.direction_tag = self.request.get('nextbus-direction-select')
            stop.stop_tag = self.request.get('nextbus-stop-select')
        stop.time_to_stop = int(self.request.get('time-to-stop'))
        max_position = stop.user.stops.order('-position').get()
        if max_position:
            stop.position = max_position.position + 1
        else:
            stop.position = 1
        stop.put()
        self.redirect('/')

class EditStop(webapp.RequestHandler):
    def get(self, id):
        '''Load the edit stop page.'''
        current_user = users.get_current_user()
        stop = models.Stop.get_by_id(int(id))
        if stop and stop.user.user == current_user:
            view.renderTemplate(self, 'edit_stop.html', { 'stop' : stop })
        else:
            self.redirect('/')

    def post(self, id):
        '''Save changes to the stop of a user.'''
        current_user = users.get_current_user()
        stop = models.Stop.get_by_id(int(id))    
        if stop and stop.user.user == current_user:
            stop.title = self.request.get('title')
            stop.agency_tag = self.request.get('agency-select')
            if stop.agency_tag == "bart":
                stop.direction_tag = self.request.get('bart-direction-select')
                stop.stop_tag = self.request.get('bart-station-select')
            else:
                stop.line_tag = self.request.get('nextbus-line-select')
                stop.direction_tag = self.request.get('nextbus-direction-select')
                stop.stop_tag = self.request.get('nextbus-stop-select')
            stop.time_to_stop = int(self.request.get('time-to-stop'))
            stop.put()
        self.redirect('/')
        
class DeleteStop(webapp.RequestHandler):
    def get(self, id):
        '''Delete a stop.'''
        current_user = users.get_current_user()
        stop = models.Stop.get_by_id(int(id))
        if stop and stop.user.user == current_user:
            stop.delete()
        self.redirect('/')
        
class MoveUp(webapp.RequestHandler):
    def get(self, id):
        '''Move a stop up in the list.'''
        current_user = users.get_current_user()
        stop = models.Stop.get_by_id(int(id))
        if stop and stop.user.user == current_user:
            other_stop = stop.user.stops.filter('position <', stop.position).order('-position').get()
            if other_stop:
                stop_position = stop.position
                stop.position = other_stop.position
                other_stop.position = stop_position
                stop.put()
                other_stop.put()
        self.redirect('/')

class MoveDown(webapp.RequestHandler):
    def get(self, id):
        '''Move a stop down in the list.'''
        current_user = users.get_current_user()
        stop = models.Stop.get_by_id(int(id))
        if stop and stop.user.user == current_user:
            other_stop = stop.user.stops.filter('position >', stop.position).order('position').get()
            if other_stop:
                stop_position = stop.position
                stop.position = other_stop.position
                other_stop.position = stop_position
                stop.put()
                other_stop.put()
        self.redirect('/')