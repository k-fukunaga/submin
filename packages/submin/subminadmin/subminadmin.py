import sys
import os

from submin.path.path import Path
from submin.models import storage

class SubminAdmin:
	def __init__(self, argv):
		self.argv = argv
		self.prompt_fmt = "Submin [%s]> "
		self.prompt = ""
		self.quit = False
		self.cmd_aliases = [('?', 'help'), ('exit', 'quit')]
		self.storage_opened = False
		self._set_systemdirs()

	def __del__(self):
		if self.storage_opened:
			try:
				storage.close()
			except storage.StorageException:
				pass # this only happens if initenv is not called yet

	def ensure_storage(self):
		if not self.storage_opened:
			storage.open()
			self.storage_opened = True

	def run(self):
		if len(self.argv) < 2:
			self.usage()
			return

		self.env = self.argv[1]
		if self.env[0] != os.path.sep:
			self.env = os.path.join(os.getcwd(), self.env)

		self.prompt = self.prompt_fmt % self.env

		# setup storage plugins
		os.environ['SUBMIN_ENV'] = self.env

		if len(self.argv) < 3:
			self.interactive()
			return

		self.execute(self.argv[2:])

	def interactive(self):
		print '''Welcome to submin-admin
Interactive Submin administration console.

Use '?' or 'help' for help on commands.
'''
		while not self.quit:
			try:
				argv = raw_input(self.prompt).split()
			except (EOFError, KeyboardInterrupt):
				print
				return

			self.execute(argv)

	def cmd_instance(self, cmd, argv):
		objname = "c_" + cmd
		try:
			X = __import__(objname, globals())
			instance = getattr(X, objname)(self, argv)
			return instance
		except (ImportError, AttributeError), e:
			print str(e)
			return None

	def commands(self):
		import glob
		import inspect
		import re

		basefile = inspect.getmodule(self).__file__
		basedir = os.path.dirname(basefile)
		pat = re.compile('c_(.*).py')
		cmds = []
		for f in glob.glob('%s/c_*.py' % basedir):
			fname = os.path.basename(f)
			cmd = re.search(pat, fname)
			cmds.append(cmd.group(1))

		cmds.sort()
		return cmds

	def cmd_alias(self, cmd):
		for tup in self.cmd_aliases:
			if tup[0] == cmd:
				return tup[1]

		return cmd

	def execute(self, argv):
		if len(argv) < 1:
			return True

		cmd = self.cmd_alias(argv[0])
		Class = self.cmd_instance(cmd, argv[1:])
		if not Class:
			print "Unknown command: %s" % ' '.join(argv)
			return True

		if not self.storage_opened:
			if not hasattr(Class, "needs_env") or Class.needs_env:
				if not os.path.exists(self.env):
					print 'environment does not exist, use initenv'
					return True

				self.ensure_storage()

		rc = Class.run()

		return rc

	def _set_systemdirs(self):
		basefile = Path(__file__)
		if not basefile.absolute:
			basefile = Path(os.getcwd()) + basefile
		# Basefile will contain <basedir>/lib/subminadmin/__init__.py
		subminadmin_basedir = basefile.dirname()
		basedir_lib = os.path.dirname(subminadmin_basedir)
		basedir = Path(basedir_lib) + 'static'
		basedir_www = basedir + 'www'
		self.basedir = basedir
		self.basedir_lib = Path(basedir_lib)
		self.basedir_www = basedir_www

	def usage(self):
		print "Usage: %s </path/to/projenv> [command [subcommand] [option]]" \
				% self.argv[0]