from django.utils import simplejson as json
from google.appengine.ext import webapp
from google.appengine.api import users
from models import models
import functions

class Agencies(webapp.RequestHandler):
    def get(self):
        '''Return the agencies.'''
        self.response.out.write(json.dumps([
            {"title": "AC Transit", "tag": "actransit"},
            {"title": "SF MUNI", "tag": "sf-muni"},
            {"title": "Metro Transit", "tag": "metrotransit"},
            {"title": "Los Angles Bus System", "tag": "lametro"},
            {"title": "Boston Bus System", "tag": "mbta"},
            {"title": "Portland Streetcar", "tag": "portland-sc"},
            {"title": "Seattle Streetcar", "tag": "seattle-sc"},
            {"title": "Toronto Bus System", "tag": "ttc"},
            {"title": "Unitrans / City of Davis", "tag": "unitrans"},
            #{"title": "BART", "tag": "bart"},
        ]))
        
class Lines(webapp.RequestHandler):
    def get(self, agency):
        '''Return the lines.'''
        self.response.out.write(json.dumps(functions.apiwrapperfor(agency).lines(agency)))
    
class Directions(webapp.RequestHandler):
    def get(self, agency, line):
        '''Return the directions.'''
        self.response.out.write(json.dumps(functions.apiwrapperfor(agency).directions(agency, line)))
            
class Stops(webapp.RequestHandler):
    def get(self, agency, line, direction):
        '''Return the stops.'''
        self.response.out.write(json.dumps(functions.apiwrapperfor(agency).stops(agency, line, direction)))

class UserLines(webapp.RequestHandler):
    def get(self):
        '''Write out data for the user's saved lines.'''
        current_user = users.get_current_user()
        if current_user:
            stops = models.User.all().filter('user =', current_user).get().stops.order('position')
        else:
            stops = default_stops()
        lineDict = {}
        for stop in stops:
            if (stop.agency_tag + " " + stop.line_tag) in lineDict.keys():
                continue
            else:
                lineDict[(stop.agency_tag + " " + stop.line_tag)] = functions.apiwrapperfor(stop.agency_tag).get_line_data(stop)
        self.response.out.write(json.dumps(lineDict.values()))

class UserStops(webapp.RequestHandler):
    def get(self):
        '''Write out the JSON for the user's saved stops.'''
        current_user = users.get_current_user()
        if current_user:
            stops = models.User.all().filter('user =', current_user).get().stops.order('position')
        else:
            stops = default_stops()
        stopList = []
        for index, stop in enumerate(stops):
            stop_data = functions.apiwrapperfor(stop.agency_tag).get_stop_data(stop)
            stopList.append({"id": stop.key().id() if stop.is_saved() else index,
                             "title": stop.title,
                             
                             "lat" : float(stop_data['lat']) if stop_data['lat'] else None,
                             "lon" : float(stop_data['lon']) if stop_data['lon'] else None,
                             
                             "agencyTag": stop.agency_tag,
                             "lineTag": stop.line_tag,
                             "directionTag": stop.direction_tag,
                             "stopTag": stop.stop_tag,
                             "destinationTag": stop.destination_tag,
                            
                             "timeToStop": stop.time_to_stop,
                             "position": stop.position,
                             "isEditable": True if stop.is_saved() else False,
            })
        self.response.out.write(json.dumps(stopList))

class UserVehicles(webapp.RequestHandler):
    def get(self, t):
        '''Write out vehicles.'''
        current_user = users.get_current_user()
        if current_user:
            stops = models.User.all().filter('user =', current_user).get().stops.order('position')
        else:
            stops = default_stops()
        lineDict = {}
        for stop in stops:
            if (stop.agency_tag + " " + stop.line_tag) in lineDict.keys():
                continue
            else:
                lineDict[(stop.agency_tag + " " + stop.line_tag)] = functions.apiwrapperfor(stop.agency_tag).get_vehicle_data(stop, t)
        self.response.out.write(json.dumps(lineDict.values()))

class UserPredictions(webapp.RequestHandler):
    def get(self):
        '''Write out the JSON predictions for the user's stops.'''
        current_user = users.get_current_user()
        if current_user:
            user = models.User.all().filter('user =', current_user).get()
            stops = user.stops.order('position')
        else:
            user = default_user()
            stops = default_stops()
        predictionList = []
        for index, stop in enumerate(stops):
            predictionList.append({ "id": stop.key().id() if stop.is_saved() else index, "directions": functions.apiwrapperfor(stop.agency_tag).get_directions(stop, user.max_arrivals, user.show_missed) })
        self.response.out.write(json.dumps(predictionList))

class UserMap(webapp.RequestHandler):
    def get(self):
        current_user = users.get_current_user()
        if current_user:
            user = models.User.all().filter('user =', current_user).get()
        else:
            user = default_user()
        self.response.out.write(json.dumps({ 'zoom' : user.zoom_level, 'lat' : user.latitude, 'lon' : user.longitude, 'mapType' : user.map_type, 'showControls' : user.show_controls }))
    
    def post(self):
        current_user = users.get_current_user()
        user = models.User.all().filter('user =', current_user).get()
        if user:
            user.zoom_level = int(self.request.get("zoom"))
            user.latitude = float(self.request.get("lat"))
            user.longitude = float(self.request.get("lon"))
            user.put()
        self.response.out.write(json.dumps({ 'saved' : True }))

def default_stops():
    the24 = models.Stop()
    the24.title = "the 24"
    the24.agency_tag = "sf-muni"
    the24.line_tag = "24"
    the24.direction_tag = "24_IB1"
    the24.stop_tag = "4326"
    the24.time_to_stop = 6
    the24.position = 1
    
    jChurch = models.Stop()
    jChurch.title = "j church at happy donut"
    jChurch.agency_tag = "sf-muni"
    jChurch.line_tag = "J"
    jChurch.direction_tag = "J__IBMTK6"
    jChurch.stop_tag = "3996"
    jChurch.time_to_stop = 12
    jChurch.position = 2
    
    return [the24, jChurch]
    
def default_user():
    user = models.User()
    user.latitude = 37.75081571576865
    user.longitude = -122.43543644302366
    user.zoom_level = 15
    user.map_type = "roadmap"
    
    user.max_arrivals = 4
    user.show_missed = True
    
    return user