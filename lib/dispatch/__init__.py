from dispatch.response import Response, HTTP404

from views.test import Test
from views.users import Users
from views.groups import Groups
from views.authviews import Login, Logout
from views.repositories import Repositories

from dispatch.session import Session

classes = {
	'test': Test,
	'users': Users,
	'groups': Groups,
	'login': Login,
	'logout': Logout,
	'repositories': Repositories(),
}

def dispatcher(request):
	# Add session information to request
	request.session = Session(request)

	path = request.path_info.strip('/').split('/')

	handlerName = 'handler'
	ajax = False
	if 'ajax' in request.post or 'ajax' in request.get:
		ajax = True

	if path[0].lower() in classes:
		cls = classes[path[0].lower()](request)
		if not hasattr(cls, handlerName):
			raise Exception, "No handler %r found for view %r" % (handlerName, path[0].lower())
		
		del path[0]
		handler = getattr(cls, handlerName)
		try:
			response = handler(request, path, ajax=ajax)
		except TypeError, e:
			if str(e).strip() != "handler() got an unexpected keyword argument 'ajax'":
				raise
			response = handler(request, path)
		
		if not issubclass(response.__class__, Response):
			raise Exception, "Handler %r should return a Response instance" % handler
		
	else:
		response = HTTP404('/'.join(path))

	request.status(response.status_code)
	request.setHeaders(response.headers)
	request.writeHeaders()
	request.write(response.content)

