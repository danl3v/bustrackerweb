from BeautifulSoup import BeautifulStoneSoup
import urllib, time

##### GENERAL #####

def get_xml(url):
    '''Go to url and returns the xml data.'''
    file = urllib.urlopen(url)
    xml = file.read()
    file.close()
    return xml

###### LINES #######

def print_lines(self, agency, selected_line=None):
    if not agency:
        return
    lines = get_xml('http://webservices.nextbus.com/service/publicXMLFeed?command=routeList&a=' + agency)
    soup = BeautifulStoneSoup(lines, selfClosingTags=['route'])
    lines = soup.findAll('route')
    self.response.out.write('<option value="">Select line...</option>')
    for line in lines:
        if line['tag'] == selected_line:
            self.response.out.write('<option value="' + line['tag'] + '" selected>' + line['title'] + '</option>')
        else:
            self.response.out.write('<option value="' + line['tag'] + '">' + line['title'] + '</option>')

###### DIRECTIONS ######

def print_directions(self, agency, line, selected_direction=None):
    if not agency or not line:
        return
    directions = get_xml('http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig&a=' + agency + '&r=' + line)
    soup = BeautifulStoneSoup(directions, selfClosingTags=['stop'])
    directions = soup.findAll('direction')
    self.response.out.write('<option value="">Select direction...</option>')
    for direction in directions:
        if direction['tag'] == selected_direction:
            self.response.out.write('<option value="' + direction['tag'] + '" selected>' + direction['title'] + '</option>')
        else:
            self.response.out.write('<option value="' + direction['tag'] + '">' + direction['title'] + '</option>')

###### STOPS ######

def print_stops(self, agency, line, direction, selected_stop=None):
    if not agency or not line or not direction:
        return
    directions = get_xml('http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig&a=' + agency + '&r=' + line)
    soup = BeautifulStoneSoup(directions, selfClosingTags=['stop'])
    stop_ids = soup.find('direction', tag=direction).findAll('stop')
    self.response.out.write('<option value="">Select stop...</option>')
    for stop_id in stop_ids:
        stop = soup.find('stop', tag=stop_id['tag'])
        if stop['tag'] == selected_stop:
            self.response.out.write('<option value="' + stop['tag'] + '" selected>' + stop['title'] + '</option>')
        else:
            self.response.out.write('<option value="' + stop['tag'] + '">' + stop['title'] + '</option>')


###### PREDICTIONS ########
    
def parse_prediction(prediction):
    '''Return a parsed a prediction.'''
    soup = BeautifulStoneSoup(prediction, selfClosingTags=['prediction'])
    predictions = soup.findAll('prediction')[:3]
    return sorted(predictions, key=lambda x: int(x['minutes']))
    
def get_leave_at(time_to_stop, minutes):
    '''Return the string that tells user when to leave to catch the bus.'''
    minutes = int(minutes)
    if time_to_stop > minutes:
        return "missed"
    elif time_to_stop == minutes:
        return "leave now"
    else:
        return "leave in " + str(minutes - time_to_stop) + "m"
    
def print_prediction(self, stop, prediction):
    '''Print a parsed prediction.'''
    predictions = parse_prediction(prediction)
    if predictions:
        for prediction in predictions:
            if prediction['minutes'] == "0":
                self.response.out.write('<tr class="time"><td class="arrival-time"><span class="big">Arriving</span></td><td class="leave-time">' + get_leave_at(stop.time_to_stop, prediction['minutes']) + '</td><tr>')
            else:
                self.response.out.write('<tr class="time"><td class="arrival-time"><span class="big">' + prediction['minutes'] + '</span> minutes</td><td class="leave-time">' + get_leave_at(stop.time_to_stop, prediction['minutes']) + '</td><tr>')
    else:
        self.response.out.write('<tr class="time"><td class="arrival-time" colspan="2">no arrivals</td><tr>')
        
def print_predictions(self, stops):
    '''Print predictionss for each of the stops.'''
    for stop in stops:
        self.response.out.write('<tr class="header"><td class="line-title">' + stop.title + '</td><td class="line-edit"><a href="/stop/edit/' +str(stop.key().id()) + '">edit</a> | <a href="/stop/delete/' +str(stop.key().id()) + '">delete</a></td></tr>')
        prediction = get_xml('http://webservices.nextbus.com/service/publicXMLFeed?command=predictions&a=' + stop.agency_tag + '&r=' + stop.line_tag + '&d=' + stop.direction_tag + '&s=' + stop.stop_tag)
        print_prediction(self, stop, prediction)