from google.appengine.ext import webapp

from BeautifulSoup import BeautifulStoneSoup
import functions

class Lines(webapp.RequestHandler):
    def post(self):
        '''Return the lines for an agency.'''
        agency = self.request.get('agency')
        selected_line = self.request.get('line')
        if not agency:
            return
        lines = functions.get_xml('http://webservices.nextbus.com/service/publicXMLFeed?command=routeList&a=' + agency)
        soup = BeautifulStoneSoup(lines, selfClosingTags=['route'])
        lines = soup.findAll('route')
        html = '<option value="">Select line...</option>'
        for line in lines:
            if line['tag'] == selected_line:
                html += '<option value="' + line['tag'] + '" selected>' + line['title'] + '</option>'
            else:
                html += '<option value="' + line['tag'] + '">' + line['title'] + '</option>'
        self.response.out.write(html)
        
class Directions(webapp.RequestHandler):
    def post(self):
        '''Return the directions for a line for an agency.'''
        agency = self.request.get('agency')
        line = self.request.get('line')
        selected_direction = self.request.get('direction')
        if not agency or not line:
            return
        directions = functions.get_xml('http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig&a=' + agency + '&r=' + line)
        soup = BeautifulStoneSoup(directions, selfClosingTags=['stop'])
        directions = soup.findAll('direction')
        html = ""
        html += '<option value="">Select direction...</option>'
        for direction in directions:
            if direction['tag'] == selected_direction:
                html += '<option value="' + direction['tag'] + '" selected>' + direction['title'] + '</option>'
            else:
                html += '<option value="' + direction['tag'] + '">' + direction['title'] + '</option>'
        self.response.out.write(html)
    
class Stops(webapp.RequestHandler):
    def post(self):
        '''Return the stops for a direction for a line for an agency.'''
        agency = self.request.get('agency')
        line = self.request.get('line')
        direction = self.request.get('direction')
        selected_stop = self.request.get('stop')
        if not agency or not line or not direction:
            return
        directions = functions.get_xml('http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig&a=' + agency + '&r=' + line)
        soup = BeautifulStoneSoup(directions, selfClosingTags=['stop'])
        stop_ids = soup.find('direction', tag=direction).findAll('stop')
        html = '<option value="">Select stop...</option>'
        for stop_id in stop_ids:
            stop = soup.find('stop', tag=stop_id['tag'])
            if stop['tag'] == selected_stop:
                html += '<option value="' + stop['tag'] + '" selected>' + stop['title'] + '</option>'
            else:
                html += '<option value="' + stop['tag'] + '">' + stop['title'] + '</option>'
        self.response.out.write(html)

def get_prediction(stop):
    '''Return a parsed prediction.'''
    soup = BeautifulStoneSoup(functions.get_xml('http://webservices.nextbus.com/service/publicXMLFeed?command=predictions&a=' + stop.agency_tag + '&r=' + stop.line_tag + '&d=' + stop.direction_tag + '&s=' + stop.stop_tag), selfClosingTags=['prediction'])
    predictions = soup.findAll('prediction')[:3]
    predictions = sorted(predictions, key=lambda x: int(x['minutes']))
    html = ""
    if predictions:
        for prediction in predictions:
            if prediction['minutes'] == "0":
                html += '<tr class="header4"><td class="header4-left"><span class="big">Arriving</span></td><td class="header4-right">' + functions.get_leave_at(stop.time_to_stop, prediction['minutes']) + '</td><tr>'
            else:
                 html += '<tr class="header4"><td class="header4-left"><span class="big">' + prediction['minutes'] + '</span> minutes</td><td class="header4-right">' + functions.get_leave_at(stop.time_to_stop, prediction['minutes']) + '</td><tr>'
    else:
         html += '<tr class="header4"><td class="header4-left" colspan="2">no arrivals</td><tr>'
    return html