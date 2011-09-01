from google.appengine.ext import webapp

from BeautifulSoup import BeautifulStoneSoup
import functions

class Stations(webapp.RequestHandler):
    def post(self):
        '''Return Bart stations.'''
        station = self.request.get('station')
        self.response.out.write(get_stations(station)) # merge this function into the class

class Directions(webapp.RequestHandler):
    def post(self):
        '''Return Bart train directions.'''
        direction = self.request.get('direction')
        self.response.out.write(get_directions(direction)) # merge this function into the class

###### DIRECTIONS ########      

def get_directions(selected_direction):
    directions = [{"name":"Both directions", "abbr":"b"}, {"name":"Northbound", "abbr":"n"}, {"name":"Southbound", "abbr":"s"}]
    html = ""
    html += '<option value="">Select direction...</option>'
    for direction in directions:
        if direction['abbr'] == selected_direction:
            html += '<option value="' + direction['abbr'] + '" selected>' + direction['name'] + '</option>'
        else:
            html += '<option value="' + direction['abbr'] + '">' + direction['name'] + '</option>'
    return html

###### STATIONS ########

def get_stations(selected_station):
    soup = BeautifulStoneSoup(functions.get_xml("http://api.bart.gov/api/stn.aspx?cmd=stns&key=MW9S-E7SL-26DU-VV8V"), selfClosingTags=[])
    stations = soup.findAll('station')
    html = ""
    html += '<option value="">Select station...</option>'
    for station in stations:
        if station.find('abbr').contents[0] == selected_station:
            html += '<option value="' + station.find('abbr').contents[0] + '" selected>' + station.find('name').contents[0] + '</option>'
        else:
            html += '<option value="' + station.find('abbr').contents[0] + '">' + station.find('name').contents[0] + '</option>'
    return html
    
###### PREDICTIONS ########
    
def get_prediction(station, direction):
    '''Return a parsed a prediction.'''
    if direction in ["n", "s"]:
        return get_prediction_helper(station, "&dir=" + direction)
    else:
    	html = ""
    	html += '<tr class="header"><td class="line-subtitle">Northbound</td><td></td></tr>'
    	html += get_prediction_helper(station, "&dir=n")
    	html += '<tr class="header"><td class="line-subtitle">Southbound</td><td></td></tr>'
    	html += get_prediction_helper(station, "&dir=s")
    	return html
    
def get_prediction_helper(station, direction):
    html = ""
    soup = BeautifulStoneSoup(functions.get_xml("http://api.bart.gov/api/etd.aspx?cmd=etd&orig=" + station + direction + "&key=MW9S-E7SL-26DU-VV8V"), selfClosingTags=[])
    routes = soup.findAll('etd')
    if routes:
		for route in routes:
			html += '<tr class="header"><td class="line-subsubtitle">' + route.destination.contents[0] + '</td><td></td></tr>'
			trains = route.findAll('estimate')
			for train in trains:
				html += '<tr class="time"><td class="arrival"><span style="height: 100%; background-color:' + train.hexcolor.contents[0] + ';">&nbsp;&nbsp;</span><span class="big">' + train.minutes.contents[0] + '</span> minutes</td><td class="leave-time">' + 'leave time fxn' + '</td><tr>'
    else:
         html += '<tr class="time"><td class="arrival-time" colspan="2">no arrivals</td><tr>'
    return html
