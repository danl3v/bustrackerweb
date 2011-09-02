from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from controllers import welcome, nextbus, bart, predictions

def main():
    application = webapp.WSGIApplication([
           ('/', welcome.MainPage),
           ('/feedback', welcome.Feedback),
           ('/predictions', predictions.Predictions),
           ('/stop/new', welcome.NewStop),
           ('/stop/edit/(.*)', welcome.EditStop),
           ('/stop/moveup/(.*)', welcome.MoveUp),
           ('/stop/movedown/(.*)', welcome.MoveDown),
           ('/stop/delete/(.*)', welcome.DeleteStop),
           ('/nextbus/lines', nextbus.Lines),
           ('/nextbus/directions', nextbus.Directions),
           ('/nextbus/stops', nextbus.Stops),
           ('/bart/stations', bart.Stations),
           ('/bart/directions', bart.Directions),
         ],debug=True)

    run_wsgi_app(application)

if __name__ == "__main__":
    main()
