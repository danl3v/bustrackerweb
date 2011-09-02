from google.appengine.ext import webapp
from google.appengine.api import users
from models import models

import nextbus, bart
    
class Predictions(webapp.RequestHandler):
    def get(self):
        '''Return the html for a line's arrival times.'''
        current_user = users.get_current_user()
        stops = models.User.all().filter('user =', current_user).get().stops.order('position')
        if stops.count() == 0:
            self.response.out.write('<tr class="header1" colspan="2"><td class="header1-left">You have no saved stops. <a href="/stop/new">Add one</a>.</td></tr>')
        else:
            self.response.out.write(get_predictions(stops))
            
def get_predictions(stops):
    '''Return formatted html predictions for each of the stops.'''
    i = 0
    html = ""
    for stop in stops:
        i += 1
        html += '<tr class="header1"><td class="header1-left">' + stop.title + '</td><td class="header1-right">'
        if i != 1: html += '<a href="/stop/moveup/' +str(stop.key().id()) + '">move up</a> | '
        if i < stops.count(): html += '<a href="/stop/movedown/' +str(stop.key().id()) + '">move down</a> | '
        html += '<a href="/stop/edit/' +str(stop.key().id()) + '">edit</a> | <a href="/stop/delete/' + str(stop.key().id()) + '">delete</a></td></tr>'
        html += get_prediction(stop)
    return html

def get_prediction(stop):
    '''Return formatted html prediction for given stop.'''
    if stop.agency_tag == "bart":
        return bart.get_prediction(stop.stop_tag, stop.direction_tag, stop.time_to_stop, stop.user.max_arrivals, stop.user.show_missed)
    else:
        return nextbus.get_prediction(stop, stop.user.max_arrivals, stop.user.show_missed)