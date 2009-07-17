from models import getBackend
import validators
backend = getBackend("user")

class UnknownUserError(Exception):
	pass

class User(object):
	@staticmethod
	def list(session_user):
		"""Returns a (sorted) list of users

		list expects a session_user argument: this is the user requesting the
		user list. If the user is not an admin, it will only get to see
		herself.
		"""
		if not session_user.is_admin: # only admins get to see the entire list
			return [session_user]     # users only see themselves

		return [User(raw_data=user) for user in backend.list()]

	@staticmethod
	def add(username):
		"""Adds a new user with a generated random password

		Raises UserExistsError if a user with this username already exists.
		"""
		# generate a random password
		from string import ascii_letters, digits
		import random
		password_chars = ascii_letters + digits
		password = ''.join([random.choice(password_chars) \
				for x in range(0, 50)])

		backend.add(username, password)

	def __init__(self, username=None, raw_data=None):
		"""Constructor, either takes a username or raw data

		If username is provided, the backend is used to get the required data.
		If raw_data is provided, the backend is not used.
		"""
		db_user = raw_data

		if not raw_data:
			db_user = backend.user_data(username)
			if not db_user:
				raise UnknownUserError(username)

		self._id       = db_user['id']
		self._name     = db_user['name']
		self._email    = db_user['email']
		self._fullname = db_user['fullname']
		self._is_admin = db_user['is_admin']

		self.member_of    = None # XXX: use Group model here?
		self.nonmember_of = None

		self.notifications = {}

		self.is_authenticated = False # used by session, listed here to provide
		                              # default value

	def __str__(self):
		return self.name

	def remove(self):
		backend.remove(self.name)

	# Properties
	def _getId(self):
		return self._id

	def _getName(self):
		return self._name

	def _getEmail(self):
		return self._email

	def _setEmail(self, email):
		self._email = email
		if not validators.validate_email(email):
			raise validators.InvalidEmail(email)
		backend.set_email(self._id, email)

	def _getFullname(self):
		return self._fullname

	def _setFullname(self, fullname):
		self._fullname = fullname
		if not validators.validate_fullname(fullname):
			raise validators.InvalidFullname(fullname)
		backend.set_fullname(self._id, fullname)

	def _getIsAdmin(self):
		return self._is_admin

	def _setIsAdmin(self, is_admin):
		self._is_admin = is_admin
		backend.set_is_admin(self._id, is_admin)

	id       = property(_getId)   # id is read-only
	name     = property(_getName) # name is read-only
	email    = property(_getEmail,    _setEmail)
	fullname = property(_getFullname, _setFullname)
	is_admin = property(_getIsAdmin,  _setIsAdmin)

__doc__ = """
Backend contract
================

* list()
	Returns a sorted list of users

* add(username, password)
	Adds a new user, raises `UserExistsError` if there already is a user with
	this username

* user_data(username)
	Returns a dictionary with all required data.
	Returns `None` if no user with this username exists.
	Fields which need to be implemented (with properties?): name, email,
	fullname, is_admin
	
* remove(username)
	Removes *username*.

* setup()
	Creates the sql-table or performs other setup

* set_email(id, email)
	Sets the email for user with id *id*

* set_fullname(id, fullname)
	Sets the fullname for user with id *id*

* set_is_admin(id, is_admin)
	Sets whether user with id *id* is an admin
"""
