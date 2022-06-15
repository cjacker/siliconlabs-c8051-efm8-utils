import exceptions

class Exception(exceptions.Exception):
	""" This class provides the Studio.Exception type for compatibility with Studio Jython. """
	pass

import running_agent
import sys
from io import TextIOWrapper

class TraceStdout:
	def write(self, string):
		running_agent.trace(string)

sys.stdout = TraceStdout()
sys.stderr = TraceStdout()
