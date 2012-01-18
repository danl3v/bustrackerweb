from google.appengine.ext import webapp
from google.appengine.runtime import DeadlineExceededError

from BeautifulSoup import BeautifulStoneSoup
import functions

def lines(agency):
    '''Return the lines for an agency.'''
    if not agency:
        return []
    try:
        lines = functions.get_xml('http://webservices.nextbus.com/service/publicXMLFeed?command=routeList&a=' + agency)
    except:
        return ["error"]
    soup = BeautifulStoneSoup(lines, selfClosingTags=['route'])
    lines = soup.findAll('route')
    list = []
    for line in lines:
        list.append({"tag" : line['tag'], "title" : line['title']})
    return list
        
def directions(agency, line):
    '''Return the directions for a line for an agency.'''
    if not agency or not line:
        return []
    try:
        directions = functions.get_xml('http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig&a=' + agency + '&r=' + line)
    except:
        return ["error"]
    soup = BeautifulStoneSoup(directions, selfClosingTags=['stop'])
    directions = soup.findAll('direction')
    list = []
    for direction in directions:
        list.append({"tag" : direction['tag'], "title" : direction['title']})
    return list
    
def stops(agency, line, direction):
    '''Return the stops for a direction for a line for an agency.'''
    if not agency or not line or not direction:
        return []
    try:
        directions = functions.get_xml('http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig&a=' + agency + '&r=' + line)
    except:
        return ["error"]
    soup = BeautifulStoneSoup(directions, selfClosingTags=['stop'])
    stop_ids = soup.find('direction', tag=direction).findAll('stop')
    list = []
    for stop_id in stop_ids:
        stop = soup.find('stop', tag=stop_id['tag'])
        list.append({"tag" : stop['tag'], "title" : stop['title']})
    return list

def get_line_data(stop):
    soup = BeautifulStoneSoup(functions.get_xml('http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig&a=' + stop.agency_tag + '&r=' + stop.line_tag), selfClosingTags=['stop', 'point'])
    route = soup.find('route')
    paths = soup.findAll('path')
    path_list = []
    for path in paths:
        points = path.findAll('point')
        point_list = []
        for point in points:
            point_list.append({ 'lat' : point['lat'], 'lon' : point['lon'] })
        path_list.append(point_list)
    return { 'title' : stop.title, 'agencyTag' : stop.agency_tag, 'lineTag': stop.line_tag, 'color' : "#" + route['color'], 'paths' : path_list }
    
def get_vehicle_data(stop, t):
    soup = BeautifulStoneSoup(functions.get_xml('http://webservices.nextbus.com/service/publicXMLFeed?command=vehicleLocations&a=' + stop.agency_tag + '&r=' + stop.line_tag + '&t=' + t), selfClosingTags=['vehicle', 'lasttime'])
    last_time = soup.find('lasttime')['time']
    vehicles = soup.findAll('vehicle')
    vehicles_list = []
    for vehicle in vehicles:
        if vehicle.has_key('dirtag'):
            directionTag = vehicle['dirtag']
        else:
            directionTag = None
        vehicles_list.append({ 'id' : vehicle['id'], 'lat' : vehicle['lat'], 'lon' : vehicle['lon'], 'heading' :  vehicle['heading'], 'directionTag' : directionTag })
    return { 'agencyTag' : stop.agency_tag, 'lineTag' : stop.line_tag, 't' : last_time, 'vehicles' : vehicles_list }

def get_stop_data(stop):
    soup = BeautifulStoneSoup(functions.get_xml('http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig&a=' + stop.agency_tag + '&r=' + stop.line_tag), selfClosingTags=['stop', 'point'])
    stops = soup.findAll('stop')
    theStop = soup.find('stop', tag=stop.stop_tag)
    return { 'agencyTag' : stop.agency_tag, 'lineTag' : stop.line_tag, 'lat' : theStop['lat'], 'lon' : theStop['lon'] }

def get_directions(stop, max_arrivals, show_missed):
    '''Return a parsed prediction.'''
    soup = BeautifulStoneSoup(functions.get_xml('http://webservices.nextbus.com/service/publicXMLFeed?command=predictions&a=' + stop.agency_tag + '&r=' + stop.line_tag + '&d=' + stop.direction_tag + '&s=' + stop.stop_tag), selfClosingTags=['prediction'])
    destinations = soup.findAll('direction')
    destinations_list = []
    for destination in destinations:
        predictions = destination.findAll('prediction')
        if not show_missed:
            predictions = filter(lambda prediction: True if functions.get_leave_at(stop.time_to_stop, prediction['minutes']) != -1 else False, predictions)
        predictions = sorted(predictions, key=lambda prediction: int(prediction['minutes']))[:max_arrivals]
        destinations_list.append({"title": destination['title'], "vehicles": [{"id" : prediction['vehicle'], "minutes" : prediction['minutes']} for prediction in predictions]})
    return [{"title": "", "destinations": destinations_list}]
