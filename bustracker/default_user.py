from models import models

def stops():
    the24 = models.Stop()
    the24.title = "the 24"
    the24.agency_tag = "sf-muni"
    the24.line_tag = "24"
    the24.direction_tag = "24_IB1"
    the24.stop_tag = "4326"
    the24.time_to_stop = 6
    the24.position = 1
    
    jChurch = models.Stop()
    jChurch.title = "j church at happy donut"
    jChurch.agency_tag = "sf-muni"
    jChurch.line_tag = "J"
    jChurch.direction_tag = "J__IBMTK6"
    jChurch.stop_tag = "3996"
    jChurch.time_to_stop = 12
    jChurch.position = 2
    
    return [the24, jChurch]
    
def user():
    user = models.User()
    user.latitude = 37.75081571576865
    user.longitude = -122.43543644302366
    user.zoom_level = 15
    user.map_type = "roadmap"
    
    user.max_arrivals = 4
    user.show_missed = True
    
    return user

user_lat = 37.750695935238916
user_lon = -122.4302528878357