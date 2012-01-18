from django.utils import simplejson as json
from google.appengine.ext import webapp
from google.appengine.runtime import DeadlineExceededError

from BeautifulSoup import BeautifulStoneSoup
import functions

def lines(agency):
    '''Return the lines for an agency.'''
    if not agency:
        return []
    try:
        lines = functions.get_xml('http://metrotransitapi.appspot.com/routes')
    except DeadlineExceededError:
        return ["error"]
    lines = json.loads(lines)
    list = []
    for line in lines:
        list.append({"tag" : line['number'], "title" : line['name']})
    return list
        
def directions(agency, line):
    '''Return the directions for a line for an agency.'''
    if not agency or not line:
        return []
    try:
        directions = functions.get_xml('http://metrotransitapi.appspot.com/direction?route=' + line)
    except DeadlineExceededError:
        return ["error"]
    directions = json.loads(directions)
    list = []
    for direction in directions:
        list.append({"tag" : str(direction['code']), "title" : direction['name']})
    return list
    
def stops(agency, line, direction):
    '''Return the stops for a direction for a line for an agency.'''
    if not agency or not line or not direction:
        return []
    try:
        stops = functions.get_xml('http://metrotransitapi.appspot.com/stops?route=' + line + '&direction=' + direction)
    except DeadlineExceededError:
        return ["error"]
    stops = sorted(json.loads(stops), key=lambda x: x['stopOrder'])
    list = []
    for stop in stops:
        list.append({"tag" : stop['code'], "title" : stop['name']})
    return list

def get_line_data(stop):
    return { 'agencyTag' : stop.agency_tag, 'lineTag' : stop.line_tag, 'paths' : [] }
    
def get_vehicle_data(stop, t):
    return None

def get_stop_data(stop):
    return { 'agencyTag' : stop.agency_tag, 'lineTag' : stop.line_tag, 'lat' : None, 'lon' : None }

def get_directions(stop, max_arrivals, show_missed):
    '''Return a parsed prediction.'''
    
    import re
    try:
    	html = functions.get_xml('http://metrotransit.org/Mobile/Nextriptext.aspx?route=' + str(stop.line_tag) + '&direction=' + str(stop.direction_tag) + '&stop=' + str(stop.stop_tag))
    except DeadlineExceededError:
        return ["error"]
    soup = BeautifulStoneSoup(html)
    current_time = soup.find('span', 'nextripCurrentTime').string[14:-3]
    (current_hours, current_minutes) = current_time.split(":")
    current_hours = int(current_hours)
    current_minutes = int(current_minutes)
    
    try:
    	predictions = json.loads(functions.get_xml('http://metrotransitapi.appspot.com/nextrip?route=' + str(stop.line_tag) + '&direction=' + str(stop.direction_tag) + '&stop=' + str(stop.stop_tag)))
    except DeadlineExceededError:
        return ["error"]
    direction = filter(lambda x: x["tag"] == stop.direction_tag, directions(stop.agency_tag, stop.line_tag))[0]
    destinations_list = []
    
    for prediction in predictions:
        if not prediction["actual"]:
            (scheduled_hours, scheduled_minutes) = prediction["time"].split(":")
            scheduled_hours = int(scheduled_hours)
            scheduled_minutes = int(scheduled_minutes)
            prediction["time"] = (scheduled_hours - current_hours)%12 * 60 + (scheduled_minutes - current_minutes)
        else:
            prediction["time"] = int(prediction['time'][:-4])
    
    if not show_missed:
        predictions = filter(lambda prediction: True if functions.get_leave_at(stop.time_to_stop, prediction['time']) != -1 else False, predictions)
    predictions = sorted(predictions, key=lambda prediction: int(prediction['time']))[:max_arrivals]
    destinations_list.append({"title": direction["title"], "vehicles": [{"id" : "0", "minutes" : prediction['time']} for prediction in predictions]})
    return [{"title": "", "destinations": destinations_list}]
