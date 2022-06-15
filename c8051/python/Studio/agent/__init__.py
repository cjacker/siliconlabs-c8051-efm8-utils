
class TCFException(Exception):
	""" This exception is thrown from TCF communications errors. """
	def __str__(self):
		return str(" ".join(_safeStr(arg) for arg in self))
	
class TimeoutException(TCFException):
	""" This exception is thrown from timeouts waiting for a command to complete. """
	def __str__(self):
		return str(" ".join(_safeStr(arg) for arg in self))
	
class CommandException(TCFException):
	""" This exception is thrown from high-level wrapping of
	TCF service commands, containing the TCF ErrorReport content. """
	def __init__(self, errorReport, command):
		TCFException.__init__(self, errorReport, command)

from _agent import *
from _channel import Message

def _safeStr(arg):
	if isinstance(arg, _agent.Command):
		arg = arg.msg
	if isinstance(arg, _channel.Message):
		return "{} {} {} {}".format(arg.token, arg.service, arg.method,
				" ".join(_safeStr(a) for a in arg.args))
	if isinstance(arg, _agent.Binary):
		return "<binary data>" 
	return str(arg) 
