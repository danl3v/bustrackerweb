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
    for line in lines[2:]:
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
    if stop.line_tag != "6":
        return
    paths = [
        [
            (44.86128, -93.35535),
            (44.860220000000005, -93.35552000000001),
            (44.859700000000004, -93.35552000000001),
            (44.85947, -93.35522),
            (44.85943, -93.35377000000001),
            (44.860060000000004, -93.35220000000001),
            (44.860440000000004, -93.35181000000001),
            (44.86101, -93.35331000000001),
            (44.86131, -93.35533000000001),
            (44.86166, -93.35879000000001),
            (44.861940000000004, -93.36130000000001),
            (44.862790000000004, -93.36282000000001),
            (44.863170000000004, -93.36387),
            (44.86536, -93.36338),
            (44.868730000000006, -93.36336000000001),
            (44.869170000000004, -93.36291000000001),
            (44.869240000000005, -93.35986000000001),
            (44.86811, -93.35967000000001),
            (44.86811, -93.35396),
            (44.86809, -93.35306000000001),
            (44.867900000000006, -93.35291000000001),
            (44.867470000000004, -93.35342000000001),
            (44.8658, -93.35394000000001),
            (44.86413, -93.35392),
            (44.86413, -93.34744),
            (44.86399, -93.34688000000001),
            (44.863580000000006, -93.34651000000001),
            (44.86332, -93.34593000000001),
            (44.863170000000004, -93.34535000000001),
            (44.86321, -93.33986),
            (44.86321, -93.33596000000001)
        ],
        [
            (44.863240000000005, -93.33589),
            (44.86554, -93.33591000000001),
            (44.86551, -93.32926),
            (44.8658, -93.32887000000001),
            (44.86822, -93.32887000000001),
            (44.868230000000004, -93.33154),
            (44.870560000000005, -93.33158),
            (44.87079000000001, -93.33145),
            (44.87095, -93.33074),
            (44.87111, -93.32969000000001),
            (44.87111, -93.32898),
            (44.874010000000006, -93.32896000000001),
            (44.874010000000006, -93.32508000000001),
            (44.87413, -93.32398),
            (44.87442, -93.32304),
            (44.87445, -93.32235000000001),
            (44.87451, -93.32124),
            (44.880430000000004, -93.32118000000001),
            (44.882130000000004, -93.32118000000001),
            (44.883190000000006, -93.32088),
            (44.884350000000005, -93.31959),
            (44.885110000000005, -93.31899000000001),
            (44.8939, -93.31882),
            (44.905080000000005, -93.31891),
            (44.92333000000001, -93.31899000000001),
            (44.92327, -93.31509000000001),
            (44.9254, -93.31434),
            (44.92701, -93.31326000000001),
            (44.927980000000005, -93.31292),
            (44.92958, -93.31324000000001),
            (44.930440000000004, -93.31298000000001),
            (44.93233, -93.31296),
            (44.93233, -93.31213000000001),
            (44.93321, -93.31092000000001),
            (44.93375, -93.30985000000001),
            (44.93441000000001, -93.30794),
            (44.93536, -93.30597),
            (44.93681, -93.30449),
            (44.937630000000006, -93.30408000000001),
            (44.937670000000004, -93.29839000000001),
            (44.94133, -93.29837),
            (44.94659, -93.29826000000001),
            (44.952160000000006, -93.29829000000001),
            (44.955450000000006, -93.29683000000001),
            (44.960840000000005, -93.29275000000001),
            (44.963080000000005, -93.29112),
            (44.965630000000004, -93.28814000000001),
            (44.970110000000005, -93.28717),
            (44.972120000000004, -93.28679000000001),
            (44.974250000000005, -93.28161),
            (44.975770000000004, -93.27801000000001),
            (44.98012000000001, -93.27182),
            (44.984440000000006, -93.26579000000001),
            (44.986290000000004, -93.26122000000001),
            (44.98796, -93.25639000000001),
            (44.986790000000006, -93.25489),
            (44.983810000000005, -93.24740000000001),
            (44.98145, -93.24144000000001),
            (44.978170000000006, -93.23326),
            (44.975120000000004, -93.22558000000001),
            (44.974720000000005, -93.22565),
            (44.97475, -93.22715000000001),
            (44.97513000000001, -93.22702000000001),
            (44.975950000000005, -93.22618000000001),
            (44.97674000000001, -93.22644000000001),
            (44.98348, -93.24331000000001),
            (44.987170000000006, -93.25251),
            (44.987700000000004, -93.25406000000001),
            (44.9885, -93.25500000000001),
            (44.989470000000004, -93.25564000000001),
            (44.988240000000005, -93.25927),
            (44.98758, -93.26015000000001),
            (44.986610000000006, -93.26124),
            (44.98621000000001, -93.26208000000001),
            (44.98442000000001, -93.26579000000001),
            (44.98377000000001, -93.26665000000001),
            (44.98456, -93.26796),
            (44.98371, -93.26901000000001),
            (44.98297, -93.26777000000001)
        ],
        [
            (44.932300000000005, -93.31298000000001),
            (44.93229, -93.31879),
            (44.93235000000001, -93.32903),
            (44.91579, -93.32905000000001),
            (44.90804000000001, -93.32905000000001),
            (44.897690000000004, -93.32905000000001),
            (44.887550000000005, -93.32894),
            (44.88568, -93.32892000000001),
            (44.88566, -93.32839000000001),
            (44.88539, -93.32770000000001),
            (44.88539, -93.32594),
            (44.883610000000004, -93.32594),
            (44.883610000000004, -93.32165),
            (44.88358, -93.32064000000001)
        ],
        [
            (44.88571, -93.3289),
            (44.88568, -93.33053000000001),
            (44.88597, -93.33156000000001),
            (44.88618, -93.33345000000001),
            (44.886790000000005, -93.33371000000001),
            (44.88884, -93.33373),
            (44.88965, -93.33409),
            (44.89021, -93.33512),
            (44.89077, -93.3366),
            (44.891560000000005, -93.33911),
            (44.893390000000004, -93.33914000000001),
            (44.89763000000001, -93.33911),
            (44.90135, -93.33918000000001),
            (44.904590000000006, -93.3392),
            (44.90529, -93.3392),
            (44.90532, -93.32905000000001)
        ],
        [
            (44.86545, -93.32881),
            (44.865480000000005, -93.32761),
            (44.864990000000006, -93.32641000000001),
            (44.865050000000004, -93.32542000000001),
            (44.86554, -93.32384),
            (44.86231, -93.32397),
            (44.86222, -93.32487),
            (44.861920000000005, -93.32551000000001),
            (44.86198, -93.33384000000001),
            (44.86274, -93.33409),
            (44.86316, -93.33478000000001),
            (44.86323, -93.33547),
            (44.863260000000004, -93.33607)
        ]
    ]
    
    path_list = []
    for path in paths:
        point_list = []
        for point in path:    
            point_list.append({"lat" : point[0], "lon" : point[1]})
        path_list.append(point_list)
    
    return { 'agencyTag' : stop.agency_tag, 'lineTag' : stop.line_tag, 'paths' : path_list }
    
def get_vehicle_data(stop, t):
    try:
        html = functions.get_xml('http://www.metrotransit.org/Mobile/NexTripText.aspx?route=' + str(stop.line_tag) + '&direction=' + str(stop.direction_tag) + '&stop=' + str(stop.stop_tag))
    except:
        return ['error']
    soup = BeautifulSoup(html)
    stop_id = soup.html.body.find('a', id='ctl00_mainContent_NexTripControl1_NexTripResults1_lnkStopNumber').string
    
    try:
        xml = functions.get_xml('http://svc.metrotransit.org/NexTrip/' + stop_id)
    except:
        return ['error']
        
    soup = BeautifulStoneSoup(xml, selfClosingTags=[])
    vehicles = soup.findAll('nextripdeparture')
    vehicles_list = []
    vehicles = filter(lambda x: "true" == x.find('actual').contents[0], vehicles)
    for vehicle in vehicles:
        vehicles_list.append({ 'id' : vehicle.find('blocknumber').contents[0], 'lat' : float(vehicle.find('vehiclelatitude').contents[0]), 'lon' : float(vehicle.find('vehiclelongitude').contents[0]), 'heading' : 0, 'directionTag' : stop.direction_tag })
    return { 'agencyTag' : stop.agency_tag, 'lineTag' : stop.line_tag, 'vehicles' : vehicles_list }

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
    
    direction = filter(lambda x: x["tag"] == stop.direction_tag, directions(stop.agency_tag, stop.line_tag))[0]
    
    predictions = []
    departTable = soup.html.body.find('div','nextripDepartures')
    if not departTable:
        return []
    rows = departTable.findAll(attrs={'class':re.compile(r'\bdata\b')})
    for row in rows:
        minutes = row.find(attrs={'class':re.compile(r'\bcol3\b')})
        actualTime = ('red' not in minutes['class'].split(' '))
        if actualTime:
            try:
                if minutes.string == "Due":
                    minutes = 0
                else:
                    minutes = int(minutes.string[:-4])
            except:
                logging.warning("PARSING BUS PREDICTION: " + str(row))
        else:
            (scheduled_hours, scheduled_minutes) = minutes.string.split(":")
            scheduled_hours = int(scheduled_hours)
            scheduled_minutes = int(scheduled_minutes)
            minutes = (scheduled_hours - current_hours)%12 * 60 + (scheduled_minutes - current_minutes)
        predictions.append({"id" : "0", "minutes": minutes})
    
    if not show_missed:
        predictions = filter(lambda prediction: True if functions.get_leave_at(stop.time_to_stop, prediction['minutes']) != -1 else False, predictions)

    predictions = sorted(predictions, key=lambda x: int(x['minutes']))[:max_arrivals]
    return [{"title": "", "destinations": [{"title": direction["title"], "vehicles": predictions}]}]