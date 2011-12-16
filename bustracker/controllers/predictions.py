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
    def get(self, agency, line, direction):
        '''Return the stops.'''
        if agency == 'bart':
            self.response.out.write(json.dumps(bart.stops(agency, line, direction)))
        else:
            self.response.out.write(json.dumps(nextbus.stops(agency, line, direction)))

class UserLines(webapp.RequestHandler):
    def get(self):
        '''Write out data for the user's saved lines.'''
        current_user = users.get_current_user()
        stops = models.User.all().filter('user =', current_user).get().stops.order('position')
        lineDict = {}
        for stop in stops:
            if (stop.agency_tag + " " + stop.line_tag) in lineDict.keys():
                continue
            else:
                lineDict[(stop.agency_tag + " " + stop.line_tag)] = nextbus.get_line_data(stop)
        self.response.out.write(json.dumps(lineDict.values()))

class UserStops(webapp.RequestHandler):
    def get(self):
        '''Write out the JSON for the user's saved stops.'''
        current_user = users.get_current_user()
        stops = models.User.all().filter('user =', current_user).get().stops.order('position')
        stopList = []
        for stop in stops:
            stop_data = nextbus.get_stop_data(stop)
            stopList.append({"id": stop.key().id(),
                             "title": stop.title,
                             
                             "lat" : float(stop_data['lat']),
                             "lon" : float(stop_data['lon']),
                             
                             "agencyTag": stop.agency_tag,
                             "lineTag": stop.line_tag,
                             "directionTag": stop.direction_tag,
                             "stopTag": stop.stop_tag,
                             "destinationTag": stop.destination_tag,
                            
                             "timeToStop": stop.time_to_stop,
                             "position": stop.position,
            })
        
        self.response.out.write(json.dumps(stopList))

class UserVehicles(webapp.RequestHandler):
    def get(self, t):
        '''Write out vehicles.'''
        current_user = users.get_current_user()
        stops = models.User.all().filter('user =', current_user).get().stops.order('position')
        lineDict = {}
        for stop in stops:
            if (stop.agency_tag + " " + stop.line_tag) in lineDict.keys():
                continue
            else:
                lineDict[(stop.agency_tag + " " + stop.line_tag)] = nextbus.get_vehicle_data(stop, t)
        self.response.out.write(json.dumps(lineDict.values()))

class UserPredictions(webapp.RequestHandler):
    def get(self):
        '''Write out the JSON predictions for the user's stops.'''
        current_user = users.get_current_user()
        stops = models.User.all().filter('user =', current_user).get().stops.order('position')
        self.response.out.write(json.dumps([
                                {   "id": stop.key().id(),
                                    "directions": get_directions(stop),
                                } for stop in stops]))

class UserMap(webapp.RequestHandler):
    def get(self):
        current_user = users.get_current_user()
        user = models.User.all().filter('user =', current_user).get()
        self.response.out.write(json.dumps({ 'zoom' : user.zoom_level, 'lat' : user.latitude, 'lon' : user.longitude, 'mapType' : user.map_type }))
    
    def post(self):
        current_user = users.get_current_user()
        user = models.User.all().filter('user =', current_user).get()
        if user:
            user.zoom_level = int(self.request.get("zoom"))
            user.latitude = float(self.request.get("lat"))
            user.longitude = float(self.request.get("lon"))
            user.put()
        self.response.out.write(json.dumps({ 'saved' : True }))
        
def get_directions(stop):
    '''Return JSON predictions for given stop.'''
    if stop.agency_tag == "bart":
        return bart.get_directions(stop.stop_tag, stop.direction_tag, stop.time_to_stop, stop.user.max_arrivals, stop.user.show_missed)
    else:
        return nextbus.get_directions(stop, stop.user.max_arrivals, stop.user.show_missed)
