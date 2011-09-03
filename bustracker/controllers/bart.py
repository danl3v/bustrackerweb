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

def get_prediction(station, direction, time_to_stop, max_arrivals, show_missed):
    '''Return a parsed a prediction.'''
    if direction in ["n", "s"]:
        return get_prediction_helper(station, "&dir=" + direction, time_to_stop, max_arrivals, show_missed)
    else:
        html = '<tr class="header2"><td class="header2-left">Northbound</td><td></td></tr>'
        html += get_prediction_helper(station, "&dir=n", time_to_stop, max_arrivals, show_missed)
        html += '<tr class="header2"><td class="header2-left">Southbound</td><td></td></tr>'
        html += get_prediction_helper(station, "&dir=s", time_to_stop, max_arrivals, show_missed)
        return html
    
def get_prediction_helper(station, direction, time_to_stop, max_arrivals, show_missed):
    '''Help return a parsed prediction.'''
    html = ""
    soup = BeautifulStoneSoup(functions.get_xml("http://api.bart.gov/api/etd.aspx?cmd=etd&orig=" + station + direction + "&key=MW9S-E7SL-26DU-VV8V"), selfClosingTags=[])
    routes = soup.findAll('etd')
    if routes:
        for route in routes:
            html += '<tr class="header3"><td class="header3-left" colspan="2">' + route.destination.contents[0] + '</td></tr>'
            trains = route.findAll('estimate')
            if not show_missed:
                trains = filter(lambda train: True if functions.get_leave_at(time_to_stop, train.minutes.contents[0]) != -1 else False, trains)
            trains = trains[:max_arrivals]
            for train in trains:
                if train.minutes.contents[0] == "Arrived":
                    html += '<tr class="header4"><td class="header4-left"><span class="big">Arriving</span></td><td class="header4-right">missed</td></tr>'
                elif train.minutes.contents[0] == "1":
                	html += '<tr class="header4"><td class="header4-left"><span class="big">' + train.minutes.contents[0] + '</span> minute</td><td class="header4-right">' + functions.get_leave_at_html(time_to_stop, int(train.minutes.contents[0])) + '</td></tr>'
                else:
                    html += '<tr class="header4"><td class="header4-left"><span class="big">' + train.minutes.contents[0] + '</span> minutes</td><td class="header4-right">' + functions.get_leave_at_html(time_to_stop, int(train.minutes.contents[0])) + '</td></tr>'
    else:
         html += '<tr class="header4"><td class="header4-left" colspan="2">no arrivals</td><tr>'
    return html
