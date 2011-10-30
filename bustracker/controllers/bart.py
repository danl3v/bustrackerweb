from google.appengine.ext import webapp

from BeautifulSoup import BeautifulStoneSoup
import functions

class Stations(webapp.RequestHandler):
    def post(self):
        '''Return Bart stations.'''
        selected_station = self.request.get('station')
        soup = BeautifulStoneSoup(functions.get_xml("http://api.bart.gov/api/stn.aspx?cmd=stns&key=MW9S-E7SL-26DU-VV8V"), selfClosingTags=[])
        stations = soup.findAll('station')
        html = '<option value="">Select station...</option>'
        for station in stations:
            if station.find('abbr').contents[0] == selected_station:
                html += '<option value="' + station.find('abbr').contents[0] + '" selected>' + station.find('name').contents[0] + '</option>'
            else:
                html += '<option value="' + station.find('abbr').contents[0] + '">' + station.find('name').contents[0] + '</option>'
        self.response.out.write(html)

class Directions(webapp.RequestHandler):
    def post(self):
        '''Return Bart train directions.'''
        selected_direction = self.request.get('direction')
        directions = [{"name":"Both directions", "abbr":"b"}, {"name":"Northbound", "abbr":"n"}, {"name":"Southbound", "abbr":"s"}]
        html = '<option value="">Select direction...</option>'
        for direction in directions:
            if direction['abbr'] == selected_direction:
                html += '<option value="' + direction['abbr'] + '" selected>' + direction['name'] + '</option>'
            else:
                html += '<option value="' + direction['abbr'] + '">' + direction['name'] + '</option>'
        self.response.out.write(html)

def get_directions(station, direction, time_to_stop, max_arrivals, show_missed):
    '''Return a parsed a prediction.'''
    if direction == "n":
        return [{"title": "Northbound", "destinations": get_destinations(station, "&dir=n", time_to_stop, max_arrivals, show_missed)}]
    elif direction == "s":
        return [{"title": "Southbound", "destinations": get_destinations(station, "&dir=s", time_to_stop, max_arrivals, show_missed)}]
    else:
        return [{"title": "Northbound", "destinations": get_destinations(station, "&dir=n", time_to_stop, max_arrivals, show_missed)},
                {"title": "Southbound", "destinations": get_destinations(station, "&dir=s", time_to_stop, max_arrivals, show_missed)}]
    
def get_destinations(station, direction, time_to_stop, max_arrivals, show_missed):
    '''Help return a parsed prediction.'''
    soup = BeautifulStoneSoup(functions.get_xml("http://api.bart.gov/api/etd.aspx?cmd=etd&orig=" + station + direction + "&key=MW9S-E7SL-26DU-VV8V"), selfClosingTags=[])
    routes = soup.findAll('etd')
    list = []
    for route in routes:
        trains = route.findAll('estimate')
        if not show_missed:
            trains = filter(lambda train: True if functions.get_leave_at(time_to_stop, train.minutes.contents[0]) != -1 else False, trains)
        trains = trains[:max_arrivals]
        list.append({"title": route.destination.contents[0], "vehicles" : [{"minutes": train.minutes.contents[0]} for train in trains]})
    return list
