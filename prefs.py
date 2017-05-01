import webapp2
import jinja2
import os
import models
import datetime
from google.appengine.api import users

template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.getcwd()))

class PrefsPage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		login_url = users.create_login_url(self.request.path)
		logout_url = users.create_logout_url(self.request.path)
		userprefs = models.get_userprefs(user.email())
		
		template = template_env.get_template('invites.html')
		invites = []
		for element in userprefs.invites:
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
	
	def post(self):
		userprefs = models.get_userprefs(users.get_current_user().email())
		try:
			initial = float(self.request.get('available.initial'))
			final = float(self.request.get('available.final'))
			userprefs.available = models.Range(initial=initial,final=final)
			userprefs.respond()
			userprefs.put()
		except ValueError:
			# User entered a value that wasn't a int. Ignore for now.
			pass
		self.redirect('/')
		
application = webapp2.WSGIApplication([('/prefs', PrefsPage)],debug=True)