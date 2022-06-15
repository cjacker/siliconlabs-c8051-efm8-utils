# Auto-generated content -- do not edit!
# If changes needed, edit RunControl.spec instead, then run siagent with "-generate".

from Studio.agent.services import *
import Studio.agent
from UserDict import UserDict

class RunControlEventListener(Studio.agent.EventListener):
	def handleEvent(self, service, eventName, arguments):
		if eventName == 'contextRemoved':
			self.onContextRemoved(*arguments)
		elif eventName == 'contextChanged':
			arguments[0] = Studio.agent._agent._wrapContexts(u'RunControl', arguments[0])
			self.onContextChanged(*arguments)
		elif eventName == 'contextAdded':
			arguments[0] = Studio.agent._agent._wrapContexts(u'RunControl', arguments[0])
			self.onContextAdded(*arguments)
		elif eventName == 'contextResumed':
			self.onContextResumed(*arguments)
		elif eventName == 'contextException':
			self.onContextException(*arguments)
		elif eventName == 'contextSuspended':
			self.onContextSuspended(*arguments)
		else: print 'Unhandled event:', service, eventName, arguments
	def onContextRemoved(self, contextIDs):
		'''
		Callback for event 'contextRemoved'.
		
		One or more contexts was removed (typically as a result of DebugAdapter#disconnect)
		@param contextIDs	
		@type contextIDs: list of Studio.agent.Context or context ID
		'''
		
		pass
	def onContextChanged(self, contexts):
		'''
		Callback for event 'contextChanged'.
		
		One or more contexts was changed
		@param contexts	
		@type contexts: list of Studio.agent.Context or property map
		'''
		
		pass
	def onContextAdded(self, contexts):
		'''
		Callback for event 'contextAdded'.
		
		One or more contexts was added (typically as a result of DebugAdapter#connect)
		@param contexts	
		@type contexts: list of Studio.agent.Context or property map
		'''
		
		pass
	def onContextResumed(self, contextID):
		'''
		Callback for event 'contextResumed'.
		
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		'''
		
		pass
	def onContextException(self, contextID, description):
		'''
		Callback for event 'contextException'.
		
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param description	
		@type description: string
		'''
		
		pass
	def onContextSuspended(self, contextID, PC, reason, stateData):
		'''
		Callback for event 'contextSuspended'.
		
		The context was suspended (either as a result of #suspend, a breakpoint, or an exception)
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param PC	
		@type PC: number
		@param reason	
		@type reason: string
		@param stateData	
		@type stateData: StateData
		'''
		
		pass

'''
(RunControlContext) Run control context ID 
'''
PROP_ID = 'ID'

'''
(RunControlContext) Context parent (owner) ID, for a thread it is same as process ID 
'''
PROP_PARENT_ID = 'ParentID'

'''
(RunControlContext) Context process (memory space) ID 
'''
PROP_PROCESS_ID = 'ProcessID'

'''
(RunControlContext) ID of a context that created this context 
'''
PROP_CREATOR_ID = 'CreatorID'

'''
(RunControlContext) Human readable context name 
'''
PROP_NAME = 'Name'

'''
(RunControlContext) true if the context is a container. Container can propagate run control commands to his children 
'''
PROP_IS_CONTAINER = 'IsContainer'

'''
(RunControlContext) true if context has execution state - can be suspended/resumed 
'''
PROP_HAS_STATE = 'HasState'

'''
(RunControlContext) Bit-set of RM_ values that are supported by the context 
'''
PROP_CAN_RESUME = 'CanResume'

'''
(RunControlContext) Bit-set of RM_ values that can be used with count > 1 
'''
PROP_CAN_COUNT = 'CanCount'

'''
(RunControlContext) true if suspend command is supported by the context
'''
PROP_CAN_SUSPEND = 'CanSuspend'

'''
(RunControlContext) true if terminate command is supported by the context 
'''
PROP_CAN_TERMINATE = 'CanTerminate'

'''
(RunControlContext) true if detach command is supported by the context 
'''
PROP_CAN_DETACH = 'CanDetach'

'''
Value for #resume: resume normally
'''
RM_RESUME = '0'

'''
Value for #resume: Step over a single instruction.
If the instruction is a function call then don't stop until the function returns.
'''
RM_STEP_OVER = '1'

'''
Value for #resume: Step a single instruction.
If the instruction is a function call then stop at first instruction of the function.
'''
RM_STEP_INTO = '2'

'''
Value for #resume: Run until control returns from current function.
'''
RM_STEP_OUT = '5'

'''
Value for #resume: Step over instructions until PC is outside the specified range.
* If any function call within the range is considered to be in range.
'''
RM_STEP_OVER_RANGE = '12'

'''
Value for #resume: Step instruction until PC is outside the specified range for any reason.
'''
RM_STEP_INTO_RANGE = '13'

'''
Value for #resume (SiAgent extension): run to one of an array of addresses ('Addresses' list in last 'resume' argument)
'''
RM_RUN_TO_ADDRESSES = '100'

'''
(contextSuspended reason) Context suspended by suspend command
'''
REASON_USER_REQUEST = 'Suspended'

'''
(contextSuspended reason) Context suspended by step command
'''
REASON_STEP = 'Step'

'''
(contextSuspended reason) Context suspended by breakpoint
'''
REASON_BREAKPOINT = 'Breakpoint'

'''
(contextSuspended reason) Context suspended by exception
'''
REASON_EXCEPTION = 'Exception'

'''
(contextSuspended reason) Context suspended as part of container
'''
REASON_CONTAINER = 'Container'

'''
(contextSuspended reason) Context suspended by watchpoint (data breakpoint)
'''
REASON_WATCHPOINT = 'Watchpoint'

'''
(contextSuspended reason) Context suspended because it received a signal
'''
REASON_SIGNAL = 'Signal'

'''
(contextSuspended reason) Context suspended because a shared library is loaded or unloaded
'''
REASON_SHAREDLIB = 'Shared Library'

'''
(contextSuspended reason) Context suspended because of an error in execution environment
'''
REASON_ERROR = 'Error'

class RunControlService(Studio.agent.Service):
	def __repr__(self):
		return '[Service ' + self.service.name + ' with ' + str(self.spec.fileName) + ']'
	
	def init(self, spec, service):
		self.spec = spec
		self.service = service
		self.eventListener = RunControlEventListener()
		self.service.addListener(self.eventListener)
	
	class Context(UserDict):
		def __init__(self, CanResume=None, CanSuspend=None, ID=None, IsContainer=None, Name=None, ParentID=None):
			UserDict.__init__(self)
			if CanResume: self['CanResume'] = CanResume
			if CanSuspend: self['CanSuspend'] = CanSuspend
			if ID: self['ID'] = ID
			if IsContainer: self['IsContainer'] = IsContainer
			if Name: self['Name'] = Name
			if ParentID: self['ParentID'] = ParentID
	
	class ResumeParams(UserDict):
		def __init__(self, Addresses=None, RangeEnd=None, RangeStart=None):
			UserDict.__init__(self)
			if Addresses: self['Addresses'] = Addresses
			if RangeEnd: self['RangeEnd'] = RangeEnd
			if RangeStart: self['RangeStart'] = RangeStart
	
	class StateData(UserDict):
		def __init__(self, message=None):
			UserDict.__init__(self)
			if message: self['message'] = message
	
	def asyncSuspend(self, contextID, done = None, progress = None):
		'''
		
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param done	Callback to invoke once command completes
		@type done: DoneSuspend
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextID: contextID = None
		if not done: done = self.__class__.DoneSuspend()
		contextID = self.spec._validateType('ContextID', contextID)
		command = self.service.sendCommand('suspend', [contextID], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneSuspend(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncSuspend'
		'''
		
		def __init__(self):
			self.command = None
		def done(self, error, args):
			if error: self.onError(error)
			else: self.onReply(*args)
		def onError(self, error):
			raise Studio.agent.CommandException(error, self.command)
		def onReply(self, error):
			if error: raise Studio.agent.CommandException(error, self.command)
	
	def syncSuspend(self, contextID, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@return SuspendReply
		'''
		
		contextID = self.spec._validateType('ContextID', contextID)
		token = self.asyncSuspend(contextID, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.SuspendReply(reply)
	
	class SuspendReply(object):
		'''
		Class containing a reply from 'syncSuspend'
		'''
		
		def __init__(self, args):
			self.values = args
		def __repr__(self):
			return str(self.values)
	
	def asyncTerminate(self, contextID, done = None, progress = None):
		'''
		
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param done	Callback to invoke once command completes
		@type done: DoneTerminate
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextID: contextID = None
		if not done: done = self.__class__.DoneTerminate()
		contextID = self.spec._validateType('ContextID', contextID)
		command = self.service.sendCommand('terminate', [contextID], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneTerminate(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncTerminate'
		'''
		
		def __init__(self):
			self.command = None
		def done(self, error, args):
			if error: self.onError(error)
			else: self.onReply(*args)
		def onError(self, error):
			raise Studio.agent.CommandException(error, self.command)
		def onReply(self, error):
			if error: raise Studio.agent.CommandException(error, self.command)
	
	def syncTerminate(self, contextID, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@return TerminateReply
		'''
		
		contextID = self.spec._validateType('ContextID', contextID)
		token = self.asyncTerminate(contextID, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.TerminateReply(reply)
	
	class TerminateReply(object):
		'''
		Class containing a reply from 'syncTerminate'
		'''
		
		def __init__(self, args):
			self.values = args
		def __repr__(self):
			return str(self.values)
	
	def asyncResume(self, contextID, mode = Studio.agent._agent._NullArg, count = Studio.agent._agent._NullArg, resume = Studio.agent._agent._NullArg, done = None, progress = None):
		'''
		
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param mode	one of RM_...
		@type mode: integer
		@param count	
		@type count: integer
		@param resume	
		@type resume: ResumeParams
		@param done	Callback to invoke once command completes
		@type done: DoneResume
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextID: contextID = None
		if not mode: mode = 0
		if not count: count = 1
		if not resume: resume = 0
		if not done: done = self.__class__.DoneResume()
		contextID = self.spec._validateType('ContextID', contextID)
		mode = self.spec._validateType('integer', mode)
		count = self.spec._validateType('integer', count)
		resume = self.spec._validateType('ResumeParams', resume)
		command = self.service.sendCommand('resume', [contextID, mode, count, resume], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneResume(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncResume'
		'''
		
		def __init__(self):
			self.command = None
		def done(self, error, args):
			if error: self.onError(error)
			else: self.onReply(*args)
		def onError(self, error):
			raise Studio.agent.CommandException(error, self.command)
		def onReply(self, error):
			if error: raise Studio.agent.CommandException(error, self.command)
	
	def syncResume(self, contextID, mode = Studio.agent._agent._NullArg, count = Studio.agent._agent._NullArg, resume = Studio.agent._agent._NullArg, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param mode	one of RM_...
		@type mode: integer
		@param count	
		@type count: integer
		@param resume	
		@type resume: ResumeParams
		@return ResumeReply
		'''
		
		contextID = self.spec._validateType('ContextID', contextID)
		mode = self.spec._validateType('integer', mode)
		count = self.spec._validateType('integer', count)
		resume = self.spec._validateType('ResumeParams', resume)
		token = self.asyncResume(contextID, mode, count, resume, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.ResumeReply(reply)
	
	class ResumeReply(object):
		'''
		Class containing a reply from 'syncResume'
		'''
		
		def __init__(self, args):
			self.values = args
		def __repr__(self):
			return str(self.values)
	
	def asyncGetContext(self, contextID, done = None, progress = None):
		'''
		
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param done	Callback to invoke once command completes
		@type done: DoneGetContext
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextID: contextID = None
		if not done: done = self.__class__.DoneGetContext()
		contextID = self.spec._validateType('ContextID', contextID)
		command = self.service.sendCommand('getContext', [contextID], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneGetContext(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncGetContext'
		'''
		
		def __init__(self):
			self.command = None
		def done(self, error, args):
			if error: self.onError(error)
			else: self.onReply(*args)
		def onError(self, error):
			raise Studio.agent.CommandException(error, self.command)
		def onReply(self, error, context):
			if error: raise Studio.agent.CommandException(error, self.command)
	
	def syncGetContext(self, contextID, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@return GetContextReply
		'''
		
		contextID = self.spec._validateType('ContextID', contextID)
		token = self.asyncGetContext(contextID, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.GetContextReply(reply)
	
	class GetContextReply(object):
		'''
		Class containing a reply from 'syncGetContext'
		'''
		
		def __init__(self, args):
			self.values = args
			self.context = Studio.agent._agent._wrapContext(u'RunControl', args[1])
		def __repr__(self):
			return str(self.values)
	
	