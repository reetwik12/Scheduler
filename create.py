import webapp2
import jinja2
import os
import models
import datetime
from google.appengine.api import users


template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.getcwd()))

class CreatePage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		login_url = users.create_login_url(self.request.path)
		logout_url = users.create_logout_url(self.request.path)
		userprefs = models.get_userprefs()
		
		template = template_env.get_template('create.html')
		context = {
		'user' : user,
		'login_url' : login_url,
		'logout_url' :logout_url,
		'userprefs' : userprefs,
		}
		self.response.out.write(template.render(context))
	
	def post(self):
		user = users.get_current_user()
		try:
			meeting = models.get_meeting()
			admin= models.get_userprefs(str(user.email()))
			admin.created.append(meeting.identify) 
			admin.put()
			
			meeting.creator = admin
			meeting.agenda = self.request.get('agenda')
			date_now = self.request.get('date').split('/')
			meeting.date = datetime.date(int(date_now[2]),int(date_now[1]),int(date_now[0]))

			meeting.duration = float(self.request.get('duration'))
			initial = float(self.request.get('time_range.initial'))
			final = float(self.request.get('time_range.final'))
			meeting.time_range = models.Range(initial=initial,final=final)
			meeting.mem_pref = []
			mems = self.request.get('mem_arg').split(',')
			for i in mems :
				mem = models.get_userprefs(i)
				new_ob = models.Mem_pref(member=mem.email)
				meeting.add(new_ob)
				mem.invites.append(meeting.identify)
			meeting.put()
			meeting.mail()
		except ValueError:
			# User entered values that were not proper. Ignore for now.
			pass
		self.redirect('/')
	
application = webapp2.WSGIApplication([('/create', CreatePage)],debug=True)