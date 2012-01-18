import logging

from django.utils import simplejson as json
from google.appengine.ext import webapp
from google.appengine.runtime import DeadlineExceededError

from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup
import functions, re

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
    try:
        html = functions.get_xml('http://www.metrotransit.org/Mobile/NexTripText.aspx?route=' + str(stop.line_tag) + '&direction=' + str(stop.direction_tag) + '&stop=' + str(stop.stop_tag))
    except:
        return ['http://www.metrotransit.org/Mobile/NexTripText.aspx?route=' + str(stop.line_tag) + '&direction=' + str(stop.direction_tag) + '&stop=' + str(stop.stop_tag)]
    soup = BeautifulSoup(html)
    current_time = soup.html.body.find('span', 'nextripCurrentTime').string[14:-3]
    (current_hours, current_minutes) = current_time.split(":")
    current_hours = int(current_hours)
    current_minutes = int(current_minutes)
    
    #direction = filter(lambda x: x["tag"] == stop.direction_tag, directions(stop.agency_tag, stop.line_tag))[0]
    
    predictions = []
    departTable = soup.html.body.find('div','nextripDepartures')
    if not departTable:
        return []
    rows = departTable.findAll(attrs={'class':re.compile(r'\bdata\b')})
    for row in rows:
        minutes = row.find(attrs={'class':re.compile(r'\bcol3\b')})
        actualTime = ('red' not in minutes['class'].split(' '))
        if actualTime:
            minutes = int(minutes.string[:-4])
        else:
            (scheduled_hours, scheduled_minutes) = minutes.string.split(":")
            scheduled_hours = int(scheduled_hours)
            scheduled_minutes = int(scheduled_minutes)
            minutes = (scheduled_hours - current_hours)%12 * 60 + (scheduled_minutes - current_minutes)
        predictions.append({"id" : "0", "minutes": minutes})
    
    if not show_missed:
        predictions = filter(lambda prediction: True if functions.get_leave_at(stop.time_to_stop, prediction['minutes']) != -1 else False, predictions)

    predictions = sorted(predictions, key=lambda x: int(x['minutes']))[:max_arrivals]
    return [{"title": "", "destinations": {"title": "test", "vehicles": predictions}}]