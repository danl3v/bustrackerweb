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
            self.response.out.write('<tr class="header" colspan="2"><td>You have no saved stops. Add one <a href="/stop/new">here</a>.</td></tr>')
        else:
            nextbus.print_predictions(self, stops)

class NewStop(webapp.RequestHandler):
    def get(self):
        '''Load the new stop page.'''
        view.renderTemplate(self, 'new_stop.html', {})
    
    def post(self):
        '''Add a new stop for a user.'''
        current_user = users.get_current_user()
        
        title = self.request.get('title')
        time_to_stop = int(self.request.get('time-to-stop'))
        user = models.User.all().filter('user =', current_user).get()
        agency_tag = self.request.get('agency-select')
        line_tag = self.request.get('line-select')
        direction_tag = self.request.get('direction-select')
        stop_tag = self.request.get('stop-select')
        
        position = user.stops.order('-position').get().position + 1
        
        stop = models.Stop()
        stop.user = user
        stop.title = title
        stop.agency_tag = agency_tag
        stop.line_tag = line_tag
        stop.direction_tag = direction_tag
        stop.stop_tag = stop_tag
        stop.time_to_stop = time_to_stop
        stop.position = position
        stop.put()
        
        self.redirect('/')

class EditStop(webapp.RequestHandler):
    def get(self, id):
        
        stop = models.Stop.get_by_id(int(id))
        view.renderTemplate(self, 'edit_stop.html', { 'stop' : stop })

    def post(self, id):
        '''Save changes to the stop of a user.'''
        current_user = users.get_current_user()
        
        title = self.request.get('title')
        time_to_stop = int(self.request.get('time-to-stop'))
        agency_tag = self.request.get('agency-select')
        line_tag = self.request.get('line-select')
        direction_tag = self.request.get('direction-select')
        stop_tag = self.request.get('stop-select')
        
        stop = models.Stop.get_by_id(int(id))
        
        if not stop.user == current_user:
            self.redirect('/')
        
        stop.title = title
        stop.agency_tag = agency_tag
        stop.line_tag = line_tag
        stop.direction_tag = direction_tag
        stop.stop_tag = stop_tag
        stop.time_to_stop = time_to_stop
        
        stop.put()
        
        self.redirect('/')
        
class DeleteStop(webapp.RequestHandler):
    def get(self, id):
        '''Delete a stop.'''
        current_user = users.get_current_user()
        stop = models.Stop.get_by_id(int(id)) # deal with stop positions
        
        if not stop.user == current_user:
            self.redirect('/')
        
        stop.delete()
        self.redirect('/')
        
class MoveUp(webapp.RequestHandler):
    def get(self, id):
        current_user = users.get_current_user()
        stop = models.Stop.get_by_id(int(id))
        
        if not stop.user == current_user:
            self.redirect('/')
        
        other_stop = stop.user.stops.filter('position <', stop.position).order('-position').get()
        
        stop_position = stop.position
        stop.position = other_stop.position
        other_stop.position = stop_position
        
        stop.put()
        other_stop.put()
        
        self.redirect('/')

class MoveDown(webapp.RequestHandler):
    def get(self, id):
        current_user = users.get_current_user()
        stop = models.Stop.get_by_id(int(id))
        
        if not stop.user == current_user:
            self.redirect('/')
        
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