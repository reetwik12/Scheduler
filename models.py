from google.appengine.api import users
from google.appengine.ext import ndb

class Range(ndb.Model):
	initial = ndb.FloatProperty(indexed=False)
	final = ndb.FloatProperty(indexed=False)

class Mem_pref(ndb.Model):
	prefs = ndb.StructuredProperty(Range)
	member = ndb.StringProperty()

class UserPrefs(ndb.Model):
	available = ndb.StructuredProperty(Range)
	email = ndb.StringProperty()
	invites = ndb.IntegerProperty(repeated=True)
	created = ndb.IntegerProperty(repeated=True)
	confirm = ndb.IntegerProperty(repeated=True)

	def respond(self):
		for invite in self.invites:
			meet = get_meeting(invite)
			for member in meet.member_pref:
				if member.member == self.email:
					member.prefs = self.available
			meet.put()

	def fix(self,identify):
		for invite in self.created:
			#if(invite == identify):
			meet = get_meeting(invite)
			meet.confirm = True
			meet.analyze()
			meet.confirm_mail()
			meet.put()

class Meeting(ndb.Model):
	"""A main model for representing an individual Meeting."""
	meet_id = 0
	identify = ndb.IntegerProperty()
	creator = ndb.StructuredProperty(UserPrefs)
	agenda = ndb.StringProperty(indexed=False)
	member_pref = ndb.StructuredProperty(Mem_pref,repeated=True) 
	date = ndb.DateProperty()
	duration = ndb.FloatProperty(indexed=False)
	time_range = ndb.StructuredProperty(Range)
	fixed = ndb.StructuredProperty(Range)
	confirm = ndb.BooleanProperty(default=False)

	def add(self,Mem):
		self.member_pref.append(Mem)

	def mail(self):
		for element in self.member_pref:
			participant = get_userprefs(str(element.member))
			participant.invites.append(self.identify) 
			participant.put()

	def confirm_mail(self):
		for element in self.member_pref:
			participant = get_userprefs(str(element.member))
			new_list = []
			for mem in participant.invites:
				if mem != self.identify:
					new_list.append(mem)
				else:
					participant.confirm.append(mem)
			participant.invites = new_list 
			participant.put()

	def analyze(self):
		slots = [0]* int((self.time_range.final - self.time_range.initial)/self.duration)
		i = self.time_range.initial
		for element in self.member_pref:
			for j in range(0,len(slots)-1):
				if( (element.prefs.initial <= i+j*self.duration)and(element.prefs.final>= i+(j+1)*self.duration) ):
					slots[j]+=1
		initial = self.time_range.initial + slots.index(max(slots))*self.duration
		final = initial + self.duration
		self.fixed = Range(initial=initial,final=final)
		
def get_userprefs(email=None):
	if not email:
		user = users.get_current_user()
		if not user:
			return None
		email = str(user.email()) 
		userprefs = UserPrefs(id=email,email=email)

	key = ndb.Key('UserPrefs',email)
	userprefs = key.get()

	if not userprefs:
		userprefs = UserPrefs(id=email,email=email)
	return userprefs

def get_meeting(meet_id=None):
	if meet_id == None:
		Meeting.meet_id+=1
		meet_id = Meeting.meet_id
		meeting = Meeting(id=meet_id)
		meeting.identify = meet_id
		return meeting

	key = ndb.Key('Meeting',meet_id)
	meeting = key.get()

	return meeting