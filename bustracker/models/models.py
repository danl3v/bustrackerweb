from google.appengine.ext import db

class User(db.Model):
    user = db.UserProperty()
    
class Stop(db.Model):
	user = db.ReferenceProperty(User, collection_name='stops')
	title = db.StringProperty(default="untitled")
	agency_tag = db.StringProperty()
	line_tag = db.StringProperty(default="")
	direction_tag = db.StringProperty()
	stop_tag = db.StringProperty()
	time_to_stop = db.IntegerProperty()
	position = db.IntegerProperty()