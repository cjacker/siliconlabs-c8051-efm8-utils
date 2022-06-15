# Auto-generated content -- do not edit!
# If changes needed, edit Memory.spec instead, then run siagent with "-generate".

from Studio.agent.services import *
import Studio.agent
from UserDict import UserDict

class MemoryEventListener(Studio.agent.EventListener):
	def handleEvent(self, service, eventName, arguments):
		if eventName == 'contextAdded':
			arguments[0] = Studio.agent._agent._wrapContexts(u'Memory', arguments[0])
			self.onContextAdded(*arguments)
		elif eventName == 'contextChanged':
			arguments[0] = Studio.agent._agent._wrapContexts(u'Memory', arguments[0])
			self.onContextChanged(*arguments)
		elif eventName == 'memoryChanged':
			self.onMemoryChanged(*arguments)
		elif eventName == 'contextRemoved':
			self.onContextRemoved(*arguments)
		else: print 'Unhandled event:', service, eventName, arguments
	def onContextAdded(self, contexts):
		'''
		Callback for event 'contextAdded'.
		
		@param contexts	
		@type contexts: list of Studio.agent.Context or property map
		'''
		
		pass
	def onContextChanged(self, contexts):
		'''
		Callback for event 'contextChanged'.
		
		@param contexts	
		@type contexts: list of Studio.agent.Context or property map
		'''
		
		pass
	def onMemoryChanged(self, contextID, ranges):
		'''
		Callback for event 'memoryChanged'.
		
		Memory content changed as a result of #set.  Sent for every affected context overlapping the original memory.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param ranges	
		@type ranges: list of AddressRange
		'''
		
		pass
	def onContextRemoved(self, contextIDs):
		'''
		Callback for event 'contextRemoved'.
		
		@param contextIDs	
		@type contextIDs: list of Studio.agent.Context or context ID
		'''
		
		pass

ACCESS_TYPE_CACHE = 'cache'

ACCESS_TYPE_DATA = 'data'

ACCESS_TYPE_HYPERVISOR = 'hypervisor'

ACCESS_TYPE_INSTRUCTION = 'instruction'

ACCESS_TYPE_IO = 'io'

ACCESS_TYPE_PHYSICAL = 'physical'

ACCESS_TYPE_SUPERVISOR = 'supervisor'

ACCESS_TYPE_TLB = 'tlb'

ACCESS_TYPE_USER = 'user'

ACCESS_TYPE_VIRTUAL = 'virtual'

BYTE_VALID = 0

BYTE_UNKNOWN = 1

BYTE_INVALID = 2

BYTE_CANNOT_READ = 4

BYTE_CANNOT_WRITE = 8

class MemoryService(Studio.agent.Service):
	def __repr__(self):
		return '[Service ' + self.service.name + ' with ' + str(self.spec.fileName) + ']'
	
	def init(self, spec, service):
		self.spec = spec
		self.service = service
		self.eventListener = MemoryEventListener()
		self.service.addListener(self.eventListener)
	
	class ErrorReport(UserDict):
		def __init__(self, AltCode=None, AltOrg=None, CausedBy=None, Code=None, Format=None, Params=None, Service=None, Severity=None, Time=None):
			UserDict.__init__(self)
			if AltCode: self['AltCode'] = AltCode
			if AltOrg: self['AltOrg'] = AltOrg
			if CausedBy: self['CausedBy'] = CausedBy
			if Code: self['Code'] = Code
			if Format: self['Format'] = Format
			if Params: self['Params'] = Params
			if Service: self['Service'] = Service
			if Severity: self['Severity'] = Severity
			if Time: self['Time'] = Time
	
	class Context(UserDict):
		def __init__(self, AccessTypes=None, AddressSize=None, BigEndian=None, End=None, ID=None, Name=None, ParentID=None, StartBound=None):
			UserDict.__init__(self)
			if AccessTypes: self['AccessTypes'] = AccessTypes
			if AddressSize: self['AddressSize'] = AddressSize
			if BigEndian: self['BigEndian'] = BigEndian
			if End: self['End'] = End
			if ID: self['ID'] = ID
			if Name: self['Name'] = Name
			if ParentID: self['ParentID'] = ParentID
			if StartBound: self['StartBound'] = StartBound
	
	class AddressRange(UserDict):
		def __init__(self, addr=None, size=None):
			UserDict.__init__(self)
			if addr: self['addr'] = addr
			if size: self['size'] = size
	
	class ErrorAddress(UserDict):
		def __init__(self, addr=None, msg=None, size=None, stat=None):
			UserDict.__init__(self)
			if addr: self['addr'] = addr
			if msg: self['msg'] = msg
			if size: self['size'] = size
			if stat: self['stat'] = stat
	
	def asyncGetChildren(self, parentContextID, done = None, progress = None):
		'''
		
		@param parentContextID	
		@type parentContextID: Studio.agent.Context or context ID
		@param done	Callback to invoke once command completes
		@type done: DoneGetChildren
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not parentContextID: parentContextID = None
		if not done: done = self.__class__.DoneGetChildren()
		parentContextID = self.spec._validateType('ContextID', parentContextID)
		command = self.service.sendCommand('getChildren', [parentContextID], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneGetChildren(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncGetChildren'
		'''
		
		def __init__(self):
			self.command = None
		def done(self, error, args):
			if error: self.onError(error)
			else: self.onReply(*args)
		def onError(self, error):
			raise Studio.agent.CommandException(error, self.command)
		def onReply(self, error, contextIDs):
			if error: raise Studio.agent.CommandException(error, self.command)
	
	def syncGetChildren(self, parentContextID, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		
		@param parentContextID	
		@type parentContextID: Studio.agent.Context or context ID
		@return GetChildrenReply
		'''
		
		parentContextID = self.spec._validateType('ContextID', parentContextID)
		token = self.asyncGetChildren(parentContextID, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.GetChildrenReply(reply)
	
	class GetChildrenReply(object):
		'''
		Class containing a reply from 'syncGetChildren'
		'''
		
		def __init__(self, args):
			self.values = args
			self.contextIDs = args[1]
		def __repr__(self):
			return str(self.values)
	
	def asyncSet(self, contextID, address, content, done = None, progress = None):
		'''
		
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param address	
		@type address: number
		@param wordSize	
		@type wordSize: integer
		@param bytes	
		@type bytes: integer
		@param mode	
		@type mode: integer
		@param content	
		@type content: binary data
		@param done	Callback to invoke once command completes
		@type done: DoneSet
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextID: contextID = None
		if not address: address = None
		wordSize = 1
		bytes = len(content)
		mode = 0
		if not content: content = None
		if not done: done = self.__class__.DoneSet()
		contextID = self.spec._validateType('ContextID', contextID)
		address = self.spec._validateType('number', address)
		content = self.spec._validateType('binary', content)
		command = self.service.sendCommand('set', [contextID, address, wordSize, bytes, mode, content], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneSet(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncSet'
		'''
		
		def __init__(self):
			self.command = None
		def done(self, error, args):
			if error: self.onError(error)
			else: self.onReply(*args)
		def onError(self, error):
			raise Studio.agent.CommandException(error, self.command)
		def onReply(self, error, errorAddresses):
			if error: raise Studio.agent.CommandException(error, self.command)
	
	def syncSet(self, contextID, address, content, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param address	
		@type address: number
		@param wordSize	
		@type wordSize: integer
		@param bytes	
		@type bytes: integer
		@param mode	
		@type mode: integer
		@param content	
		@type content: binary data
		@return SetReply
		'''
		
		contextID = self.spec._validateType('ContextID', contextID)
		address = self.spec._validateType('number', address)
		content = self.spec._validateType('binary', content)
		token = self.asyncSet(contextID, address, content, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.SetReply(reply)
	
	class SetReply(object):
		'''
		Class containing a reply from 'syncSet'
		'''
		
		def __init__(self, args):
			self.values = args
			self.errorAddresses = args[1]
		def __repr__(self):
			return str(self.values)
	
	def asyncGet(self, contextID, address, bytes, done = None, progress = None):
		'''
		
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param address	
		@type address: number
		@param wordSize	
		@type wordSize: integer
		@param bytes	
		@type bytes: integer
		@param mode	
		@type mode: integer
		@param done	Callback to invoke once command completes
		@type done: DoneGet
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextID: contextID = None
		if not address: address = None
		wordSize = 1
		if not bytes: bytes = None
		mode = 0
		if not done: done = self.__class__.DoneGet()
		contextID = self.spec._validateType('ContextID', contextID)
		address = self.spec._validateType('number', address)
		bytes = self.spec._validateType('integer', bytes)
		command = self.service.sendCommand('get', [contextID, address, wordSize, bytes, mode], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneGet(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncGet'
		'''
		
		def __init__(self):
			self.command = None
		def done(self, error, args):
			if error: self.onError(error)
			else: self.onReply(*args)
		def onError(self, error):
			raise Studio.agent.CommandException(error, self.command)
		def onReply(self, content, error, errorAddresses):
			if error: raise Studio.agent.CommandException(error, self.command)
	
	def syncGet(self, contextID, address, bytes, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param address	
		@type address: number
		@param wordSize	
		@type wordSize: integer
		@param bytes	
		@type bytes: integer
		@param mode	
		@type mode: integer
		@return GetReply
		'''
		
		contextID = self.spec._validateType('ContextID', contextID)
		address = self.spec._validateType('number', address)
		bytes = self.spec._validateType('integer', bytes)
		token = self.asyncGet(contextID, address, bytes, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.GetReply(reply)
	
	class GetReply(object):
		'''
		Class containing a reply from 'syncGet'
		'''
		
		def __init__(self, args):
			self.values = args
			self.content = args[0]
			self.errorAddresses = args[2]
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
			self.context = Studio.agent._agent._wrapContext(u'Memory', args[1])
		def __repr__(self):
			return str(self.values)
	
	