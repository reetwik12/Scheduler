import webapp2
import jinja2
import os
import models
import datetime
from google.appengine.api import users

template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.getcwd()))

class Schedule(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		login_url = users.create_login_url(self.request.path)
		logout_url = users.create_logout_url(self.request.path)
		userprefs = models.get_userprefs()
		
		template = template_env.get_template('schedule.html')
		invites = []
		for element in userprefs.confirm:
			new_obj = models.get_meeting(element)
			invites.append(new_obj)
		context = {
		'user' : user,
		'login_url' : login_url,
		'logout_url' :logout_url,
		'userprefs' : userprefs,
		'invites' : invites,
		}
		self.response.out.write(template.render(context))
	
application = webapp2.WSGIApplication([('/schedule', Schedule)],debug=True)