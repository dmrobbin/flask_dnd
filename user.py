class User:
	user_id =0
	user_name='Not Logged In'
	authenticated =False
	active = False
	anonymous = False

	def __init__(self):
		user_id=0
		user_name='none'

	def login(self, new_id, u_name):
		self.user_id=new_id
		self.user_name=u_name

	def logout(self):
		self.user_id=0
		self.user_name='Not Logged In'

	def get_id(self):
		return self.user_id

	def get_Name(self):
		return self.user_name

	def is_authenticated(self):
		return self.authenticated

	def is_active(self):
		return self.active
 
	def is_anonymous(self):
		return self.anonymous