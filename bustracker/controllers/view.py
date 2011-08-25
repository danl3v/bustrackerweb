import os

from google.appengine.dist import use_library
from google.appengine.api import users
use_library('django', '1.2')

from google.appengine.ext.webapp import template

def getHeaderFooterData(self):
    '''Get and return the template values to render the header and footer which are standard on all pages. Also sets standard data across all pages.'''
    current_user = users.get_current_user()
    if current_user:
        login_url = users.create_logout_url("/")
        login_url_linktext = 'logout'
    else:
        login_url = users.create_login_url(self.request.uri)
        login_url_linktext = 'login'

    template_values =  {
        'current_user': current_user,
        'login_url': login_url,
        'login_url_linktext': login_url_linktext
        }

    return template_values

def renderTemplate(self, template_file, template_values):
    '''Render a template with its values and send the data to the browser.'''
    template_values = dict(getHeaderFooterData(self), **template_values)
    path = os.path.join(os.path.dirname(__file__), '../views/' + template_file)
    self.response.out.write(template.render(path, template_values))