from google.appengine.ext import webapp
from google.appengine.api import users
from models import models
import view


class SaveStop(webapp.RequestHandler):
    def post(self):
        '''Add or edit a stop.'''
        current_user = users.get_current_user()
        id = self.request.get('id')
        if id:
            stop = models.Stop.get_by_id(int(id))
        else:
            stop = models.Stop()
            stop.user = models.User.all().filter('user =', current_user).get()
        
        if stop and stop.user.user == current_user:
            stop.title = self.request.get('title')
            stop.agency_tag = self.request.get('agencyTag')
            if stop.agency_tag == "bart":
                stop.direction_tag = self.request.get('bart-direction-select')
                stop.stop_tag = self.request.get('bart-station-select')
            else:
                stop.line_tag = self.request.get('lineTag')
                stop.direction_tag = self.request.get('directionTag')
                stop.stop_tag = self.request.get('stopTag')
            stop.time_to_stop = int(self.request.get('timeToStop'))
            stop.position = 0
            key = stop.put()
            self.response.out.write('{"id": ' + str(key.id()) + '}')
        
class DeleteStop(webapp.RequestHandler):
    def post(self):
        '''Delete a stop.'''
        current_user = users.get_current_user()
        id = self.request.get('id')
        stop = models.Stop.get_by_id(int(id))
        if stop and stop.user.user == current_user:
            stop.delete()
        self.response.out.write('{"id": ' + str(id) + '}')
        
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