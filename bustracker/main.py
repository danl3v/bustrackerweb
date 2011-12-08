from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from controllers import welcome, stops, nextbus, bart, predictions, posts

def main():
    application = webapp.WSGIApplication([
           # main
           ('/', welcome.MainPage),
           ('/feedback', welcome.Feedback),
           ('/settings', welcome.Settings),
           
           # user specific data
           ('/stops', predictions.UserStops),
           ('/predictions', predictions.UserPredictions),
           
           # stop management
		   ('/stop/save', stops.SaveStop),
           ('/stop/moveup/(.*)', stops.MoveUp),
           ('/stop/movedown/(.*)', stops.MoveDown),
           ('/stop/delete', stops.DeleteStop),
           
           # general api
           ('/agencies', predictions.Agencies),
           ('/(.*)/lines', predictions.Lines),
           ('/(.*)/(.*)/directions', predictions.Directions),
           ('/(.*)/(.*)/(.*)/stops', predictions.Stops),
           
           # bart
           ('/bart/stations', bart.Stations),
           ('/bart/directions', bart.Directions),
           
           # news feed
           ('/posts', posts.Posts),
           ('/post/new', posts.NewPost),
           ('/post/edit/(.*)', posts.EditPost),
           ('/post/delete/(.*)', posts.DeletePost),
           
         ],debug=True)

    run_wsgi_app(application)

if __name__ == "__main__":
    main()
