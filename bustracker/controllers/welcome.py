from google.appengine.ext import webapp
from google.appengine.api import users
from models import models
import view, nextbus

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

class Predictions(webapp.RequestHandler):
    def get(self):
        '''Return the html for a line's arrival times.'''
        current_user = users.get_current_user()
        stops = models.User.all().filter('user =', current_user).get().stops.order('position')
        if stops.count() == 0:
            self.response.out.write('<tr class="header" colspan="2"><td class="line-title">You have no saved stops. <a href="/stop/new">Add one</a>.</td></tr>')
        else:
            nextbus.print_predictions(self, stops)

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
        stop.line_tag = self.request.get('line-select')
        stop.direction_tag = self.request.get('direction-select')
        stop.stop_tag = self.request.get('stop-select')
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
            stop.line_tag = self.request.get('line-select')
            stop.direction_tag = self.request.get('direction-select')
            stop.stop_tag = self.request.get('stop-select')
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

class Lines(webapp.RequestHandler):
    def post(self):
        '''Return the lines for an agency.'''
        agency = self.request.get('agency')
        line = self.request.get('line')
        nextbus.print_lines(self, agency, line)
        
class Directions(webapp.RequestHandler):
    def post(self):
        '''Return the directions for a line for an agency.'''
        agency = self.request.get('agency')
        line = self.request.get('line')
        direction = self.request.get('direction')
        nextbus.print_directions(self, agency, line, direction)
    
class Stops(webapp.RequestHandler):
    def post(self):
        '''Return the directions for a line for an agency.'''
        agency = self.request.get('agency')
        line = self.request.get('line')
        direction = self.request.get('direction')
        stop = self.request.get('stop')
        nextbus.print_stops(self, agency, line, direction, stop)