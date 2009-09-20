from bootstrap import fimport, settings, SettingsException, setSettings
from models.exceptions import BackendAlreadySetup, BackendError

def get(model):
	"""Gets the backend-module for a certain model."""
	try:
		backend = fimport("plugins.backends.%s.%s" % (settings.backend, model),
			       "plugins.backends.%s" % settings.backend)
	except SettingsException, e:
		raise BackendError(str(e))

	return backend

def setup():
	"""Calls setup, this is usually only done when initialising the environment
	or a new backend is used."""

	# Calls plugins.backends.<backend>.setup()
	try:
		fimport("plugins.backends.%s" % settings.backend,
				"plugins.backends").setup()
	except SettingsException, e:
		raise BackendError(str(e))

def open(pass_settings=None):
	"""opens the backend: either opens a database connection or does
	other initialisation."""
	if pass_settings:
		setSettings(pass_settings)

	try:
		fimport("plugins.backends.%s" % settings.backend,
				"plugins.backends").open(settings)
	except SettingsException, e:
		raise BackendError(str(e))

def close():
	"""close() will close databases, if approriate."""
	try:
		fimport("plugins.backends.%s" % settings.backend,
				"plugins.backends").close()
	except SettingsException, e:
		raise BackendError(str(e))
