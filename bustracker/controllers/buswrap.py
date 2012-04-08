from django.utils import simplejson as json
from google.appengine.ext import webapp
from google.appengine.api import users
from models import models
import functions
import default_user

class Agencies(webapp.RequestHandler):
    def get(self):
        '''Return the agencies.'''
        self.response.out.write(json.dumps([
            {"title": "AC Transit", "tag": "actransit"},
            {"title": "SF MUNI", "tag": "sf-muni"},
            #{"title": "Metro Transit", "tag": "metrotransit"},
            #{"title": "Los Angles Bus System", "tag": "lametro"},
            #{"title": "Boston Bus System", "tag": "mbta"},
            #{"title": "Portland Streetcar", "tag": "portland-sc"},
            #{"title": "Seattle Streetcar", "tag": "seattle-sc"},
            #{"title": "Toronto Bus System", "tag": "ttc"},
            #{"title": "Unitrans / City of Davis", "tag": "unitrans"},
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
            stops = default_user.stops()
        lineDict = {}
        for stop in stops:
            if (stop.agency_tag + " " + stop.line_tag) in lineDict.keys():
                continue
            else:
                try:
                    lineDict[(stop.agency_tag + " " + stop.line_tag)] = functions.apiwrapperfor(stop.agency_tag).get_line_data(stop)
                except:
                    lineDict[(stop.agency_tag + " " + stop.line_tag)] = "error"
        self.response.out.write(json.dumps(lineDict.values()))

class UserStops(webapp.RequestHandler):
    def get(self):
        '''Write out the JSON for the user's saved stops.'''
        current_user = users.get_current_user()
        if current_user:
            user = models.User.all().filter('user =', current_user).get()
            if user:
                stops = user.stops.order('position')
            else:
                return
        else:
            stops = default_user.stops()
        stopList = []
        for index, stop in enumerate(stops):
            try:
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
            except:
                stopList.append({"error" : True})
        self.response.out.write(json.dumps(stopList))

class UserVehicles(webapp.RequestHandler):
    def get(self, t):
        '''Write out vehicles.'''
        current_user = users.get_current_user()
        if current_user:
            stops = models.User.all().filter('user =', current_user).get().stops.order('position')
        else:
            stops = default_user.stops()
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
            if user:
                stops = user.stops.order('position')
            else:
                return
        else:
            user = default_user.user()
            stops = default_user.stops()
        predictionList = []
        for index, stop in enumerate(stops):
            predictionList.append({ "id": stop.key().id() if stop.is_saved() else index, "directions": functions.apiwrapperfor(stop.agency_tag).get_directions(stop, user.max_arrivals, user.show_missed) })
        self.response.out.write(json.dumps(predictionList))

class UserMap(webapp.RequestHandler):
    def get(self):
        current_user = users.get_current_user()
        if current_user:
            user = models.User.all().filter('user =', current_user).get()
            user_lat = None
            user_lon = None
        else:
            user = default_user.user()
            user_lat = default_user.user_lat
            user_lon = default_user.user_lon
        self.response.out.write(json.dumps({
                        'zoom' : user.zoom_level,
                        'lat' : user.latitude,
                        'lon' : user.longitude,
                        'mapType' : user.map_type,
                        'showControls' : user.show_controls,
                        'user_lat' : user_lat,
                        'user_lon' : user_lon,
                        }))
    
    def post(self):
        current_user = users.get_current_user()
        user = models.User.all().filter('user =', current_user).get()
        if user:
            user.zoom_level = int(self.request.get("zoom"))
            user.latitude = float(self.request.get("lat"))
            user.longitude = float(self.request.get("lon"))
            user.put()
        self.response.out.write(json.dumps({ 'saved' : True }))
        