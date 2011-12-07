from django.utils import simplejson as json
from google.appengine.ext import webapp
from google.appengine.api import users
from models import models

import nextbus, bart

class Agencies(webapp.RequestHandler):
    def get(self):
        '''Return the agencies.'''
        self.response.out.write(json.dumps([
            {"title": "AC Transit", "tag": "actransit"},
            {"title": "SF MUNI", "tag": "sf-muni"},
            #{"title": "BART", "tag": "bart"},
        ]))
        
class Lines(webapp.RequestHandler):
    def get(self, agency):
        '''Return the lines.'''
        if agency == 'bart':
            self.response.out.write(json.dumps(bart.lines(agency)))
        else:
            self.response.out.write(json.dumps(nextbus.lines(agency)))
    
class Directions(webapp.RequestHandler):
    def get(self, agency, line):
        '''Return the directions.'''
        if agency == 'bart':
            self.response.out.write(json.dumps(bart.directions(agency, line)))
        else:
            self.response.out.write(json.dumps(nextbus.directions(agency, line)))

class Stops(webapp.RequestHandler):
    def get(self):
        '''Write out the JSON for the user's saved stops.'''
        current_user = users.get_current_user()
        stops = models.User.all().filter('user =', current_user).get().stops.order('position')
        self.response.out.write(json.dumps([
                                {   "id": stop.key().id(),
                                    "title": stop.title,
                                    
                                    "agencyTag": stop.agency_tag,
                                    "lineTag": stop.line_tag,
                                    "directionTag": stop.direction_tag,
                                    "stopTag": stop.stop_tag,
                                    "destinationTag": stop.destination_tag,
                                    
                                    "timeToStop": stop.time_to_stop,
                                    "position": stop.position,
                                } for stop in stops]))

class Predictions(webapp.RequestHandler):
    def get(self):
        '''Write out the JSON predictions for the user's stops.'''
        current_user = users.get_current_user()
        stops = models.User.all().filter('user =', current_user).get().stops.order('position')
        self.response.out.write(json.dumps([
                                {   "id": stop.key().id(),
                                    "directions": get_directions(stop),
                                } for stop in stops]))

def get_directions(stop):
    '''Return JSON predictions for given stop.'''
    if stop.agency_tag == "bart":
        return bart.get_directions(stop.stop_tag, stop.direction_tag, stop.time_to_stop, stop.user.max_arrivals, stop.user.show_missed)
    else:
        return nextbus.get_directions(stop, stop.user.max_arrivals, stop.user.show_missed)
