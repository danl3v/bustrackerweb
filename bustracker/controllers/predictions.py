import nextbus, bart
    
def get_predictions(stops):
    '''Return formatted html predictions for each of the stops.'''
    i = 0
    html = ""
    for stop in stops:
        i += 1
        html += '<tr class="header"><td class="line-title">' + stop.title + '</td><td class="line-edit">'
        if i != 1: html += '<a href="/stop/moveup/' +str(stop.key().id()) + '">move up</a> | '
        if i < stops.count(): html += '<a href="/stop/movedown/' +str(stop.key().id()) + '">move down</a> | '
        html += '<a href="/stop/edit/' +str(stop.key().id()) + '">edit</a> | <a href="/stop/delete/' + str(stop.key().id()) + '">delete</a></td></tr>'
        html += get_prediction(stop)
    return html

def get_prediction(stop):
    '''Return formatted html prediction for given stop.'''
    if stop.agency_tag == "bart":
        return bart.get_prediction(stop.stop_tag, stop.direction_tag, stop.time_to_stop)
    else:
        return nextbus.get_prediction(stop)