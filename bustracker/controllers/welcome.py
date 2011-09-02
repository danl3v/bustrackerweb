from google.appengine.ext import webapp
from google.appengine.api import users
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
            view.renderTemplate(self, 'predictions.html', {})
        else:
            view.renderTemplate(self, 'index.html', {})

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
        if stop.user.user == current_user:
            view.renderTemplate(self, 'edit_stop.html', { 'stop' : stop })
        else:
            self.redirect('/')

    def post(self, id):
        '''Save changes to the stop of a user.'''
        current_user = users.get_current_user()
        stop = models.Stop.get_by_id(int(id))    
        if stop.user.user == current_user:
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
        if stop.user.user == current_user:
            stop.delete()
        self.redirect('/')
        
class MoveUp(webapp.RequestHandler):
    def get(self, id):
        '''Move a stop up in the list.'''
        current_user = users.get_current_user()
        stop = models.Stop.get_by_id(int(id))
        if stop.user.user == current_user:
            other_stop = stop.user.stops.filter('position <', stop.position).order('-position').get()
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
        if stop.user.user == current_user:
            other_stop = stop.user.stops.filter('position >', stop.position).order('-position').get()
            stop_position = stop.position
            stop.position = other_stop.position
            other_stop.position = stop_position
            stop.put()
            other_stop.put()
        self.redirect('/')