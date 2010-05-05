import os

from submin.dispatch.view import View
from submin.dispatch.response import Response, Redirect
from submin.views.error import ErrorResponse
from submin.template.shortcuts import evaluate
from submin.models.exceptions import NoMD5PasswordError, UnknownUserError
from submin.models import user
from submin.models import options
from submin.models.storage import database_isuptodate

class Login(View):
	def handler(self, request, path):
		if not request.post:
			return self.evaluate_form()
		username = request.post.get('username', '')
		password = request.post.get('password', '')

		invalid_login = True
		u = None
		try:
			u = user.User(username)
			invalid_login = False
		except UnknownUserError, e:
			pass

		try:
			if not u or not u.check_password(password):
				return self.evaluate_form('Not a valid username and password combination')
		except NoMD5PasswordError, e:
			return self.evaluate_form(config, str(e))

		if invalid_login:
			return self.evaluate_form('Not a valid username and password combination')

		url = options.url_path('base_url_submin')
		if 'redirected_from' in request.session:
			url = request.session['redirected_from']

		if not database_isuptodate():
			localvalues = {}
			request.session['upgrade_user'] = True
			base_url = options.value('base_url_submin')
			localvalues['base_url'] = base_url
			localvalues['session_user'] = u
			return Response(evaluate('database_upgrade.html', localvalues))

		u.is_authenticated = True
		request.session['user'] = u
		request.session.save()

		return Redirect(url)


	def evaluate_form(self, msg=''):
		localvalues = {}
		localvalues['msg'] = msg
		base_url = options.value('base_url_submin')
		if base_url[-1] != '/':
			base_url += '/'
		localvalues['base_url'] = base_url
		return Response(evaluate('login.html', localvalues))


class Logout(View):
	def handler(self, request, path):
		if 'user' in request.session:
			request.session['user'].is_authenticated = False
			del request.session['user']
		url = '/'
		if 'redirected_from' in request.session:
			url = request.session['redirected_from']
		return Redirect(url)
