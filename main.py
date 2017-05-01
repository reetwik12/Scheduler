import datetime
import jinja2
import os
import webapp2
import models

from google.appengine.api import users

template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.getcwd()))

class MainPage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		login_url = users.create_login_url(self.request.path)
		logout_url = users.create_logout_url(self.request.path)
		userprefs = models.get_userprefs()

		template = template_env.get_template('index.html')
		context = {
		'user' : user,
		'login_url' : login_url,
		'logout_url' :logout_url,
		'userprefs' : userprefs,
		}
		self.response.out.write(template.render(context))
application = webapp2.WSGIApplication([('/',MainPage)],debug=True)