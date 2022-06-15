# Auto-generated content -- do not edit!
# If changes needed, edit DebugAdapter.spec instead, then run siagent with "-generate".

from Studio.agent.services import *
import Studio.agent
from UserDict import UserDict

class DebugAdapterEventListener(Studio.agent.EventListener):
	def handleEvent(self, service, eventName, arguments):
		if eventName == 'contextAdded':
			arguments[0] = Studio.agent._agent._wrapContexts(u'DebugAdapter', arguments[0])
			self.onContextAdded(*arguments)
		elif eventName == 'contextChanged':
			arguments[0] = Studio.agent._agent._wrapContexts(u'DebugAdapter', arguments[0])
			self.onContextChanged(*arguments)
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
	def onContextRemoved(self, contextIDs):
		'''
		Callback for event 'contextRemoved'.
		
		@param contextIDs	
		@type contextIDs: list of Studio.agent.Context or context ID
		'''
		
		pass

CONNECT_METHOD_ATTACH = 'attach'

CONNECT_METHOD_NORMAL = 'normal'

RESET_TYPE_DEFAULT = 'default'

J_LINK_SPEED_ADAPTIVE = 'adaptive'

J_LINK_SPEED_AUTO = 'auto'

'''
The unique ID of a context
'''
PROP_ID = 'ID'

'''
The human-readable name of a context
'''
PROP_NAME = 'Name'

'''
The ID of the parent to this context
'''
PROP_PARENT_ID = 'ParentID'

'''
Option for #connectStream (int) -- rate (in Hz) to send Streams#read responses; 0 means send as soon as possible
'''
OPTION_READ_RATE = 'readRate'

'''
Option for #connectStream (int) -- rate (in Hz) to send data chunks to the port; 0 means send as soon as possible (default)
'''
OPTION_WRITE_RATE = 'writeRate'

'''
the adapter type (TYPE_...)
'''
PROP_TYPE = 'Type'

'''
the adapter type (TYPE_...)
'''
TYPE_UNKNOWN = 'Unknown'

TYPE_UDA = 'UDA'

TYPE_EC3 = 'EC3'

TYPE_TOOLSTICK = 'Toolstick'

TYPE_J_LINK = 'J-Link'

VID_SILICON_LABS = '10c4'

PID_USB_DEBUG_ADAPTER = '8044'

PID_UDA_DEBUG_ADAPTER = '8045'

PID_TOOLSTICK = '8253'

'''
enum: target interface for device connection (TARGET_INTERFACE_...) (J-Link adapters only)
'''
PROP_TYPE = 'TargetInterface'

'''
enum: target interface for device connection (TARGET_INTERFACE_...) (J-Link adapters only)
'''
PROP_TARGET_INTERFACE = 'TargetInterface'

TARGET_INTERFACE_SWD = 'swd'

TARGET_INTERFACE_JTAG = 'jtag'

TARGET_INTERFACE_C2 = 'c2'

'''
Option for #connect (array of strings) -- local path to .json file(s) describing the device memory/registers/etc.
'''
OPTION_DEVICE_DESCRIPTOR_PATHS = 'deviceDescriptorPaths'

'''
Option for #connect (enum) -- the method used to connect to a device (CONNECT_TYPE_...)
'''
OPTION_CONNECT_METHOD = 'connectMethod'

'''
enum value: normal connect method
'''
CONNECT_METHOD_NORMAL = 'normal'

'''
enum value: attach connect method (no reset) 
'''
CONNECT_METHOD_ATTACH = 'attach'

'''
Option for #connect (boolean) -- if true, only connect to a device, do not establish debug-capable connection
'''
OPTION_NO_DEBUGGING = 'noDebugging'

'''
Option for #connect (bitmask) (ARM): exceptions to catch, issuing RunControl#contextSuspended events
'''
PROP_EXCEPTIONS_TO_CATCH = 'exceptionsToCatch'

'''
(PROP_EXCEPTIONS_TO_CATCH) bitmask value
'''
ARM_CORTEX_M_VC_CORERESET = '1'

'''
(PROP_EXCEPTIONS_TO_CATCH) bitmask value
'''
ARM_CORTEX_M_VC_MMERR = '16'

'''
(PROP_EXCEPTIONS_TO_CATCH) bitmask value
'''
ARM_CORTEX_M_VC_NOCPERR = '32'

'''
(PROP_EXCEPTIONS_TO_CATCH) bitmask value
'''
ARM_CORTEX_M_VC_CHKERR = '64'

'''
(PROP_EXCEPTIONS_TO_CATCH) bitmask value
'''
ARM_CORTEX_M_VC_STATERR = '128'

'''
(PROP_EXCEPTIONS_TO_CATCH) bitmask value
'''
ARM_CORTEX_M_VC_BUSERR = '256'

'''
(PROP_EXCEPTIONS_TO_CATCH) bitmask value
'''
ARM_CORTEX_M_VC_INTERR = '512'

'''
(PROP_EXCEPTIONS_TO_CATCH) bitmask value
'''
ARM_CORTEX_M_VC_HARDERR = '1024'

'''
Option for #setConfigOptions (J-Link)
'''
PROP_ADDRESSING_MODE = 'addressingMode'

ADDRESSING_MODE_SERIAL = 'serial'

ADDRESSING_MODE_USB_PREFIX = 'usb'

ADDRESSING_MODE_USB_0 = 'usb0'

ADDRESSING_MODE_USB_1 = 'usb1'

ADDRESSING_MODE_USB_2 = 'usb2'

ADDRESSING_MODE_USB_3 = 'usb3'

'''
Option for #setConfigOptions (J-Link)
'''
PROP_DEBUG_MODE = 'debugMode'

DEBUG_MODE_MCU = 'mcu'

DEBUG_MODE_IN = 'in'

DEBUG_MODE_OUT = 'out'

DEBUG_MODE_OFF = 'off'

class DebugAdapterService(Studio.agent.Service):
	def __repr__(self):
		return '[Service ' + self.service.name + ' with ' + str(self.spec.fileName) + ']'
	
	def init(self, spec, service):
		self.spec = spec
		self.service = service
		self.eventListener = DebugAdapterEventListener()
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
	
	class ConnectStreamOptions(UserDict):
		def __init__(self, readRate=None, writeRate=None):
			UserDict.__init__(self)
			if readRate: self['readRate'] = readRate
			if writeRate: self['writeRate'] = writeRate
	
	class ConfigOptions(UserDict):
		def __init__(self, baudRate=None, connectMethod=None, coreSpeed=None, deviceDescriptorPaths=None, enableITM=None, exceptionsToCatch=None, jLinkSpeed=None, noDebugging=None, resetType=None):
			UserDict.__init__(self)
			if baudRate: self['baudRate'] = baudRate
			if connectMethod: self['connectMethod'] = connectMethod
			if coreSpeed: self['coreSpeed'] = coreSpeed
			if deviceDescriptorPaths: self['deviceDescriptorPaths'] = deviceDescriptorPaths
			if enableITM: self['enableITM'] = enableITM
			if exceptionsToCatch: self['exceptionsToCatch'] = exceptionsToCatch
			if jLinkSpeed: self['jLinkSpeed'] = jLinkSpeed
			if noDebugging: self['noDebugging'] = noDebugging
			if resetType: self['resetType'] = resetType
	
	class Device(UserDict):
		def __init__(self, Family=None, ID=None):
			UserDict.__init__(self)
			if Family: self['Family'] = Family
			if ID: self['ID'] = ID
	
	def asyncRefreshChildren(self, contextID, done = None, progress = None):
		'''
		Refresh the children of this context, to remove any obsolete ones or add any new ones.  Changes are reported via EventListener#contextAdded or #contextRemoved callbacks.  Still-existing children are not updated.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param done	Callback to invoke once command completes
		@type done: DoneRefreshChildren
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextID: contextID = None
		if not done: done = self.__class__.DoneRefreshChildren()
		contextID = self.spec._validateType('ContextID', contextID)
		command = self.service.sendCommand('refreshChildren', [contextID], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneRefreshChildren(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncRefreshChildren'
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
	
	def syncRefreshChildren(self, contextID, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		Refresh the children of this context, to remove any obsolete ones or add any new ones.  Changes are reported via EventListener#contextAdded or #contextRemoved callbacks.  Still-existing children are not updated.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@return RefreshChildrenReply
		'''
		
		contextID = self.spec._validateType('ContextID', contextID)
		token = self.asyncRefreshChildren(contextID, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.RefreshChildrenReply(reply)
	
	class RefreshChildrenReply(object):
		'''
		Class containing a reply from 'syncRefreshChildren'
		'''
		
		def __init__(self, args):
			self.values = args
		def __repr__(self):
			return str(self.values)
	
	def asyncAddContext(self, parentID, id, properties, done = None, progress = None):
		'''
		Dynamically add the given context to the context tree,returning its generated PROP_ID (usually parentID + '.' + id).
		The generated context will have PROP_PARENT_ID == parentID,PROP_NAME == subID (if not otherwise specified in 'properties'),and PROP_ID == the returned contextID. 
		It is an error if a context already exists with the generated PROP_ID,but that generated ID is returned for examination.
		Once added, this fires the 'contextAdded' event.
		@param parentID	The parent into which to create the context
		@type parentID: Studio.agent.Context or context ID
		@param id	The full ID (if it contains '.') or the suffix of parentID + '.'
		@type id: string
		@param properties	Additional properties to set on the context
		@type properties: dict of names to values
		@param done	Callback to invoke once command completes
		@type done: DoneAddContext
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not parentID: parentID = None
		if not id: id = None
		if not properties: properties = None
		if not done: done = self.__class__.DoneAddContext()
		parentID = self.spec._validateType('ContextID', parentID)
		id = self.spec._validateType('string', id)
		properties = self.spec._validateType('object', properties)
		command = self.service.sendCommand('addContext', [parentID, id, properties], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneAddContext(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncAddContext'
		'''
		
		def __init__(self):
			self.command = None
		def done(self, error, args):
			if error: self.onError(error)
			else: self.onReply(*args)
		def onError(self, error):
			raise Studio.agent.CommandException(error, self.command)
		def onReply(self, error, contextID):
			if error: raise Studio.agent.CommandException(error, self.command)
	
	def syncAddContext(self, parentID, id, properties, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		Dynamically add the given context to the context tree,returning its generated PROP_ID (usually parentID + '.' + id).
		The generated context will have PROP_PARENT_ID == parentID,PROP_NAME == subID (if not otherwise specified in 'properties'),and PROP_ID == the returned contextID. 
		It is an error if a context already exists with the generated PROP_ID,but that generated ID is returned for examination.
		Once added, this fires the 'contextAdded' event.
		@param parentID	The parent into which to create the context
		@type parentID: Studio.agent.Context or context ID
		@param id	The full ID (if it contains '.') or the suffix of parentID + '.'
		@type id: string
		@param properties	Additional properties to set on the context
		@type properties: dict of names to values
		@return AddContextReply
		'''
		
		parentID = self.spec._validateType('ContextID', parentID)
		id = self.spec._validateType('string', id)
		properties = self.spec._validateType('object', properties)
		token = self.asyncAddContext(parentID, id, properties, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.AddContextReply(reply)
	
	class AddContextReply(object):
		'''
		Class containing a reply from 'syncAddContext'
		'''
		
		def __init__(self, args):
			self.values = args
			self.contextID = args[1]
		def __repr__(self):
			return str(self.values)
	
	def asyncRefresh(self, contextID, force, done = None, progress = None):
		'''
		Refresh this context to update its properties.  Sends an EventListener#contextChanged callback or reports an error (possibly with a #contextRemoved event) if the context is no longer valid.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param force	
		@type force: boolean
		@param done	Callback to invoke once command completes
		@type done: DoneRefresh
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextID: contextID = None
		if not force: force = None
		if not done: done = self.__class__.DoneRefresh()
		contextID = self.spec._validateType('ContextID', contextID)
		force = self.spec._validateType('boolean', force)
		command = self.service.sendCommand('refresh', [contextID, force], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneRefresh(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncRefresh'
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
	
	def syncRefresh(self, contextID, force, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		Refresh this context to update its properties.  Sends an EventListener#contextChanged callback or reports an error (possibly with a #contextRemoved event) if the context is no longer valid.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param force	
		@type force: boolean
		@return RefreshReply
		'''
		
		contextID = self.spec._validateType('ContextID', contextID)
		force = self.spec._validateType('boolean', force)
		token = self.asyncRefresh(contextID, force, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.RefreshReply(reply)
	
	class RefreshReply(object):
		'''
		Class containing a reply from 'syncRefresh'
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
			self.context = Studio.agent._agent._wrapContext(u'DebugAdapter', args[1])
		def __repr__(self):
			return str(self.values)
	
	def asyncGetChildren(self, parentContextID, done = None, progress = None):
		'''
		Retrieve children of given context.  This fetches the last known list.  It should return immediately.
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
		Retrieve children of given context.  This fetches the last known list.  It should return immediately.
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
	
	def asyncStopListeningChildren(self, contextID, done = None, progress = None):
		'''
		Disable automatic detection of children for the given context. If the previous #startListeningChildren call specified to recurse, this removes listeners automatically added by that call. 
		Calls to #startListeningChildren and #stopListeningChildren must be balanced.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param done	Callback to invoke once command completes
		@type done: DoneStopListeningChildren
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextID: contextID = None
		if not done: done = self.__class__.DoneStopListeningChildren()
		contextID = self.spec._validateType('ContextID', contextID)
		command = self.service.sendCommand('stopListeningChildren', [contextID], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneStopListeningChildren(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncStopListeningChildren'
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
	
	def syncStopListeningChildren(self, contextID, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		Disable automatic detection of children for the given context. If the previous #startListeningChildren call specified to recurse, this removes listeners automatically added by that call. 
		Calls to #startListeningChildren and #stopListeningChildren must be balanced.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@return StopListeningChildrenReply
		'''
		
		contextID = self.spec._validateType('ContextID', contextID)
		token = self.asyncStopListeningChildren(contextID, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.StopListeningChildrenReply(reply)
	
	class StopListeningChildrenReply(object):
		'''
		Class containing a reply from 'syncStopListeningChildren'
		'''
		
		def __init__(self, args):
			self.values = args
		def __repr__(self):
			return str(self.values)
	
	def asyncRemoveContext(self, contextID, done = None, progress = None):
		'''
		Dynamically remove the given context from the context tree.
		Once removed, this fires the 'contextRemoved' event.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param done	Callback to invoke once command completes
		@type done: DoneRemoveContext
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextID: contextID = None
		if not done: done = self.__class__.DoneRemoveContext()
		contextID = self.spec._validateType('ContextID', contextID)
		command = self.service.sendCommand('removeContext', [contextID], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneRemoveContext(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncRemoveContext'
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
	
	def syncRemoveContext(self, contextID, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		Dynamically remove the given context from the context tree.
		Once removed, this fires the 'contextRemoved' event.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@return RemoveContextReply
		'''
		
		contextID = self.spec._validateType('ContextID', contextID)
		token = self.asyncRemoveContext(contextID, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.RemoveContextReply(reply)
	
	class RemoveContextReply(object):
		'''
		Class containing a reply from 'syncRemoveContext'
		'''
		
		def __init__(self, args):
			self.values = args
		def __repr__(self):
			return str(self.values)
	
	def asyncAddOrChangeContext(self, contextProperties, done = None, progress = None):
		'''
		Dynamically add or change the given context in the context tree.
		If not existing, fires a 'contextAdded' event.  Else, this fires the 'contextChanged' event.
		@param contextProperties	the full set of context properties (including PROP_ID, PROP_PARENT_ID, PROP_NAME)
		@type contextProperties: dict of names to values
		@param done	Callback to invoke once command completes
		@type done: DoneAddOrChangeContext
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextProperties: contextProperties = None
		if not done: done = self.__class__.DoneAddOrChangeContext()
		contextProperties = self.spec._validateType('object', contextProperties)
		command = self.service.sendCommand('addOrChangeContext', [contextProperties], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneAddOrChangeContext(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncAddOrChangeContext'
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
	
	def syncAddOrChangeContext(self, contextProperties, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		Dynamically add or change the given context in the context tree.
		If not existing, fires a 'contextAdded' event.  Else, this fires the 'contextChanged' event.
		@param contextProperties	the full set of context properties (including PROP_ID, PROP_PARENT_ID, PROP_NAME)
		@type contextProperties: dict of names to values
		@return AddOrChangeContextReply
		'''
		
		contextProperties = self.spec._validateType('object', contextProperties)
		token = self.asyncAddOrChangeContext(contextProperties, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.AddOrChangeContextReply(reply)
	
	class AddOrChangeContextReply(object):
		'''
		Class containing a reply from 'syncAddOrChangeContext'
		'''
		
		def __init__(self, args):
			self.values = args
		def __repr__(self):
			return str(self.values)
	
	def asyncChangeContext(self, contextProperties, done = None, progress = None):
		'''
		Dynamically change the given context in the context tree.
		Once changed, this fires the 'contextChanged' event.
		@param contextProperties	the full set of context properties (including PROP_ID, PROP_PARENT_ID, PROP_NAME)
		@type contextProperties: dict of names to values
		@param done	Callback to invoke once command completes
		@type done: DoneChangeContext
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextProperties: contextProperties = None
		if not done: done = self.__class__.DoneChangeContext()
		contextProperties = self.spec._validateType('object', contextProperties)
		command = self.service.sendCommand('changeContext', [contextProperties], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneChangeContext(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncChangeContext'
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
	
	def syncChangeContext(self, contextProperties, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		Dynamically change the given context in the context tree.
		Once changed, this fires the 'contextChanged' event.
		@param contextProperties	the full set of context properties (including PROP_ID, PROP_PARENT_ID, PROP_NAME)
		@type contextProperties: dict of names to values
		@return ChangeContextReply
		'''
		
		contextProperties = self.spec._validateType('object', contextProperties)
		token = self.asyncChangeContext(contextProperties, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.ChangeContextReply(reply)
	
	class ChangeContextReply(object):
		'''
		Class containing a reply from 'syncChangeContext'
		'''
		
		def __init__(self, args):
			self.values = args
		def __repr__(self):
			return str(self.values)
	
	def asyncGetFilteredChildren(self, parentContextID, properties, done = None, progress = None):
		'''
		Retrieve filtered children of given context.  This works from the last known list.  It should return immediately.
		@param parentContextID	
		@type parentContextID: Studio.agent.Context or context ID
		@param properties	
		@type properties: dict of names to values
		@param done	Callback to invoke once command completes
		@type done: DoneGetFilteredChildren
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not parentContextID: parentContextID = None
		if not properties: properties = None
		if not done: done = self.__class__.DoneGetFilteredChildren()
		parentContextID = self.spec._validateType('ContextID', parentContextID)
		properties = self.spec._validateType('object', properties)
		command = self.service.sendCommand('getFilteredChildren', [parentContextID, properties], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneGetFilteredChildren(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncGetFilteredChildren'
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
	
	def syncGetFilteredChildren(self, parentContextID, properties, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		Retrieve filtered children of given context.  This works from the last known list.  It should return immediately.
		@param parentContextID	
		@type parentContextID: Studio.agent.Context or context ID
		@param properties	
		@type properties: dict of names to values
		@return GetFilteredChildrenReply
		'''
		
		parentContextID = self.spec._validateType('ContextID', parentContextID)
		properties = self.spec._validateType('object', properties)
		token = self.asyncGetFilteredChildren(parentContextID, properties, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.GetFilteredChildrenReply(reply)
	
	class GetFilteredChildrenReply(object):
		'''
		Class containing a reply from 'syncGetFilteredChildren'
		'''
		
		def __init__(self, args):
			self.values = args
			self.contextIDs = args[1]
		def __repr__(self):
			return str(self.values)
	
	def asyncStartListeningChildren(self, contextID, pollTime, recurse, done = None, progress = None):
		'''
		Enable automatic detection of children for the given context. This will result in #contextAdded, #contextRemoved, and #contextChanged events as the service polls for changes. 
		Calls to #startListeningChildren and #stopListeningChildren must be balanced.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param pollTime	
		@type pollTime: integer
		@param recurse	
		@type recurse: boolean
		@param done	Callback to invoke once command completes
		@type done: DoneStartListeningChildren
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextID: contextID = None
		if not pollTime: pollTime = None
		if not recurse: recurse = True
		if not done: done = self.__class__.DoneStartListeningChildren()
		contextID = self.spec._validateType('ContextID', contextID)
		pollTime = self.spec._validateType('integer', pollTime)
		recurse = self.spec._validateType('boolean', recurse)
		command = self.service.sendCommand('startListeningChildren', [contextID, pollTime, recurse], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneStartListeningChildren(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncStartListeningChildren'
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
	
	def syncStartListeningChildren(self, contextID, pollTime, recurse, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		Enable automatic detection of children for the given context. This will result in #contextAdded, #contextRemoved, and #contextChanged events as the service polls for changes. 
		Calls to #startListeningChildren and #stopListeningChildren must be balanced.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param pollTime	
		@type pollTime: integer
		@param recurse	
		@type recurse: boolean
		@return StartListeningChildrenReply
		'''
		
		contextID = self.spec._validateType('ContextID', contextID)
		pollTime = self.spec._validateType('integer', pollTime)
		recurse = self.spec._validateType('boolean', recurse)
		token = self.asyncStartListeningChildren(contextID, pollTime, recurse, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.StartListeningChildrenReply(reply)
	
	class StartListeningChildrenReply(object):
		'''
		Class containing a reply from 'syncStartListeningChildren'
		'''
		
		def __init__(self, args):
			self.values = args
		def __repr__(self):
			return str(self.values)
	
	def asyncDisconnectStream(self, contextID, streamType, done = None, progress = None):
		'''
		Disconnect from the given streams for the given context id, disposing the associated streams.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param streamType	
		@type streamType: string
		@param done	Callback to invoke once command completes
		@type done: DoneDisconnectStream
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextID: contextID = None
		if not streamType: streamType = None
		if not done: done = self.__class__.DoneDisconnectStream()
		contextID = self.spec._validateType('ContextID', contextID)
		streamType = self.spec._validateType('string', streamType)
		command = self.service.sendCommand('disconnectStream', [contextID, streamType], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneDisconnectStream(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncDisconnectStream'
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
	
	def syncDisconnectStream(self, contextID, streamType, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		Disconnect from the given streams for the given context id, disposing the associated streams.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param streamType	
		@type streamType: string
		@return DisconnectStreamReply
		'''
		
		contextID = self.spec._validateType('ContextID', contextID)
		streamType = self.spec._validateType('string', streamType)
		token = self.asyncDisconnectStream(contextID, streamType, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.DisconnectStreamReply(reply)
	
	class DisconnectStreamReply(object):
		'''
		Class containing a reply from 'syncDisconnectStream'
		'''
		
		def __init__(self, args):
			self.values = args
		def __repr__(self):
			return str(self.values)
	
	def asyncGetSupportedStreamTypes(self, contextID, done = None, progress = None):
		'''
		Get the list of Streams type ids available for the adapter.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param done	Callback to invoke once command completes
		@type done: DoneGetSupportedStreamTypes
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextID: contextID = None
		if not done: done = self.__class__.DoneGetSupportedStreamTypes()
		contextID = self.spec._validateType('ContextID', contextID)
		command = self.service.sendCommand('getSupportedStreamTypes', [contextID], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneGetSupportedStreamTypes(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncGetSupportedStreamTypes'
		'''
		
		def __init__(self):
			self.command = None
		def done(self, error, args):
			if error: self.onError(error)
			else: self.onReply(*args)
		def onError(self, error):
			raise Studio.agent.CommandException(error, self.command)
		def onReply(self, error, streamTypes):
			if error: raise Studio.agent.CommandException(error, self.command)
	
	def syncGetSupportedStreamTypes(self, contextID, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		Get the list of Streams type ids available for the adapter.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@return GetSupportedStreamTypesReply
		'''
		
		contextID = self.spec._validateType('ContextID', contextID)
		token = self.asyncGetSupportedStreamTypes(contextID, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.GetSupportedStreamTypesReply(reply)
	
	class GetSupportedStreamTypesReply(object):
		'''
		Class containing a reply from 'syncGetSupportedStreamTypes'
		'''
		
		def __init__(self, args):
			self.values = args
			self.streamTypes = args[1]
		def __repr__(self):
			return str(self.values)
	
	def asyncConnectStream(self, contextID, streamType, options, done = None, progress = None):
		'''
		Connect to the given stream for the given adapter id, returning Streams identifiers to channel the data.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param streamType	
		@type streamType: string
		@param options	
		@type options: ConnectStreamOptions
		@param done	Callback to invoke once command completes
		@type done: DoneConnectStream
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextID: contextID = None
		if not streamType: streamType = None
		if not options: options = None
		if not done: done = self.__class__.DoneConnectStream()
		contextID = self.spec._validateType('ContextID', contextID)
		streamType = self.spec._validateType('string', streamType)
		options = self.spec._validateType('ConnectStreamOptions', options)
		command = self.service.sendCommand('connectStream', [contextID, streamType, options], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneConnectStream(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncConnectStream'
		'''
		
		def __init__(self):
			self.command = None
		def done(self, error, args):
			if error: self.onError(error)
			else: self.onReply(*args)
		def onError(self, error):
			raise Studio.agent.CommandException(error, self.command)
		def onReply(self, error, inputStreamId, outputStreamId):
			if error: raise Studio.agent.CommandException(error, self.command)
	
	def syncConnectStream(self, contextID, streamType, options, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		Connect to the given stream for the given adapter id, returning Streams identifiers to channel the data.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param streamType	
		@type streamType: string
		@param options	
		@type options: ConnectStreamOptions
		@return ConnectStreamReply
		'''
		
		contextID = self.spec._validateType('ContextID', contextID)
		streamType = self.spec._validateType('string', streamType)
		options = self.spec._validateType('ConnectStreamOptions', options)
		token = self.asyncConnectStream(contextID, streamType, options, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.ConnectStreamReply(reply)
	
	class ConnectStreamReply(object):
		'''
		Class containing a reply from 'syncConnectStream'
		'''
		
		def __init__(self, args):
			self.values = args
			self.inputStreamId = args[1]
			self.outputStreamId = args[2]
		def __repr__(self):
			return str(self.values)
	
	def asyncSetConfigOptions(self, contextID, options, done = None, progress = None):
		'''
		Set one or more options to configure the adapter.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param options	
		@type options: dict of names to values
		@param done	Callback to invoke once command completes
		@type done: DoneSetConfigOptions
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextID: contextID = None
		if not options: options = None
		if not done: done = self.__class__.DoneSetConfigOptions()
		contextID = self.spec._validateType('ContextID', contextID)
		options = self.spec._validateType('object', options)
		command = self.service.sendCommand('setConfigOptions', [contextID, options], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneSetConfigOptions(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncSetConfigOptions'
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
	
	def syncSetConfigOptions(self, contextID, options, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		Set one or more options to configure the adapter.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param options	
		@type options: dict of names to values
		@return SetConfigOptionsReply
		'''
		
		contextID = self.spec._validateType('ContextID', contextID)
		options = self.spec._validateType('object', options)
		token = self.asyncSetConfigOptions(contextID, options, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.SetConfigOptionsReply(reply)
	
	class SetConfigOptionsReply(object):
		'''
		Class containing a reply from 'syncSetConfigOptions'
		'''
		
		def __init__(self, args):
			self.values = args
		def __repr__(self):
			return str(self.values)
	
	def asyncGetConfigOptions(self, contextID, done = None, progress = None):
		'''
		Get the values for all the configurable adapter options.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param done	Callback to invoke once command completes
		@type done: DoneGetConfigOptions
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextID: contextID = None
		if not done: done = self.__class__.DoneGetConfigOptions()
		contextID = self.spec._validateType('ContextID', contextID)
		command = self.service.sendCommand('getConfigOptions', [contextID], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneGetConfigOptions(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncGetConfigOptions'
		'''
		
		def __init__(self):
			self.command = None
		def done(self, error, args):
			if error: self.onError(error)
			else: self.onReply(*args)
		def onError(self, error):
			raise Studio.agent.CommandException(error, self.command)
		def onReply(self, error, options):
			if error: raise Studio.agent.CommandException(error, self.command)
	
	def syncGetConfigOptions(self, contextID, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		Get the values for all the configurable adapter options.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@return GetConfigOptionsReply
		'''
		
		contextID = self.spec._validateType('ContextID', contextID)
		token = self.asyncGetConfigOptions(contextID, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.GetConfigOptionsReply(reply)
	
	class GetConfigOptionsReply(object):
		'''
		Class containing a reply from 'syncGetConfigOptions'
		'''
		
		def __init__(self, args):
			self.values = args
			self.options = args[1]
		def __repr__(self):
			return str(self.values)
	
	def asyncGetConfigOptionType(self, contextID, optionID, done = None, progress = None):
		'''
		Get the type of a configurable adapter option.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param optionID	
		@type optionID: string
		@param done	Callback to invoke once command completes
		@type done: DoneGetConfigOptionType
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextID: contextID = None
		if not optionID: optionID = None
		if not done: done = self.__class__.DoneGetConfigOptionType()
		contextID = self.spec._validateType('ContextID', contextID)
		optionID = self.spec._validateType('string', optionID)
		command = self.service.sendCommand('getConfigOptionType', [contextID, optionID], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneGetConfigOptionType(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncGetConfigOptionType'
		'''
		
		def __init__(self):
			self.command = None
		def done(self, error, args):
			if error: self.onError(error)
			else: self.onReply(*args)
		def onError(self, error):
			raise Studio.agent.CommandException(error, self.command)
		def onReply(self, error, type):
			if error: raise Studio.agent.CommandException(error, self.command)
	
	def syncGetConfigOptionType(self, contextID, optionID, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		Get the type of a configurable adapter option.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param optionID	
		@type optionID: string
		@return GetConfigOptionTypeReply
		'''
		
		contextID = self.spec._validateType('ContextID', contextID)
		optionID = self.spec._validateType('string', optionID)
		token = self.asyncGetConfigOptionType(contextID, optionID, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.GetConfigOptionTypeReply(reply)
	
	class GetConfigOptionTypeReply(object):
		'''
		Class containing a reply from 'syncGetConfigOptionType'
		'''
		
		def __init__(self, args):
			self.values = args
			self.type = args[1]
		def __repr__(self):
			return str(self.values)
	
	def asyncGetSupportedConfigOptions(self, contextID, done = None, progress = None):
		'''
		Get the list of configurable adapter option IDs.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param done	Callback to invoke once command completes
		@type done: DoneGetSupportedConfigOptions
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextID: contextID = None
		if not done: done = self.__class__.DoneGetSupportedConfigOptions()
		contextID = self.spec._validateType('ContextID', contextID)
		command = self.service.sendCommand('getSupportedConfigOptions', [contextID], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneGetSupportedConfigOptions(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncGetSupportedConfigOptions'
		'''
		
		def __init__(self):
			self.command = None
		def done(self, error, args):
			if error: self.onError(error)
			else: self.onReply(*args)
		def onError(self, error):
			raise Studio.agent.CommandException(error, self.command)
		def onReply(self, error, optionIDs):
			if error: raise Studio.agent.CommandException(error, self.command)
	
	def syncGetSupportedConfigOptions(self, contextID, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		Get the list of configurable adapter option IDs.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@return GetSupportedConfigOptionsReply
		'''
		
		contextID = self.spec._validateType('ContextID', contextID)
		token = self.asyncGetSupportedConfigOptions(contextID, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.GetSupportedConfigOptionsReply(reply)
	
	class GetSupportedConfigOptionsReply(object):
		'''
		Class containing a reply from 'syncGetSupportedConfigOptions'
		'''
		
		def __init__(self, args):
			self.values = args
			self.optionIDs = args[1]
		def __repr__(self):
			return str(self.values)
	
	def asyncDisconnect(self, contextID, done = None, progress = None):
		'''
		
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param done	Callback to invoke once command completes
		@type done: DoneDisconnect
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextID: contextID = None
		if not done: done = self.__class__.DoneDisconnect()
		contextID = self.spec._validateType('ContextID', contextID)
		command = self.service.sendCommand('disconnect', [contextID], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneDisconnect(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncDisconnect'
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
	
	def syncDisconnect(self, contextID, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@return DisconnectReply
		'''
		
		contextID = self.spec._validateType('ContextID', contextID)
		token = self.asyncDisconnect(contextID, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.DisconnectReply(reply)
	
	class DisconnectReply(object):
		'''
		Class containing a reply from 'syncDisconnect'
		'''
		
		def __init__(self, args):
			self.values = args
		def __repr__(self):
			return str(self.values)
	
	def asyncConnect(self, properties, done = None, progress = None):
		'''
		Connect to a device.
		If successful, triggers a DeviceSupport#contextChanged event on the device actually connected,in which the PROP_CONNECTED value changes. 
		Also triggers a RunControl#contextAdded event for a new RunControlContext.
		@param properties	
		@type properties: dict of names to values
		@param done	Callback to invoke once command completes
		@type done: DoneConnect
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not properties: properties = None
		if not done: done = self.__class__.DoneConnect()
		properties = self.spec._validateType('object', properties)
		command = self.service.sendCommand('connect', [properties], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneConnect(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncConnect'
		'''
		
		def __init__(self):
			self.command = None
		def done(self, error, args):
			if error: self.onError(error)
			else: self.onReply(*args)
		def onError(self, error):
			raise Studio.agent.CommandException(error, self.command)
		def onReply(self, error, device):
			if error: raise Studio.agent.CommandException(error, self.command)
	
	def syncConnect(self, properties, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		Connect to a device.
		If successful, triggers a DeviceSupport#contextChanged event on the device actually connected,in which the PROP_CONNECTED value changes. 
		Also triggers a RunControl#contextAdded event for a new RunControlContext.
		@param properties	
		@type properties: dict of names to values
		@return ConnectReply
		'''
		
		properties = self.spec._validateType('object', properties)
		token = self.asyncConnect(properties, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.ConnectReply(reply)
	
	class ConnectReply(object):
		'''
		Class containing a reply from 'syncConnect'
		'''
		
		def __init__(self, args):
			self.values = args
			self.device = args[1]
		def __repr__(self):
			return str(self.values)
	
	def asyncGetConfigOptionType(self, contextID, optionID, done = None, progress = None):
		'''
		Get the type of a #connect option.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param optionID	
		@type optionID: string
		@param done	Callback to invoke once command completes
		@type done: DoneGetConfigOptionType
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextID: contextID = None
		if not optionID: optionID = None
		if not done: done = self.__class__.DoneGetConfigOptionType()
		contextID = self.spec._validateType('ContextID', contextID)
		optionID = self.spec._validateType('string', optionID)
		command = self.service.sendCommand('getConfigOptionType', [contextID, optionID], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneGetConfigOptionType(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncGetConfigOptionType'
		'''
		
		def __init__(self):
			self.command = None
		def done(self, error, args):
			if error: self.onError(error)
			else: self.onReply(*args)
		def onError(self, error):
			raise Studio.agent.CommandException(error, self.command)
		def onReply(self, error, type):
			if error: raise Studio.agent.CommandException(error, self.command)
	
	def syncGetConfigOptionType(self, contextID, optionID, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		Get the type of a #connect option.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param optionID	
		@type optionID: string
		@return GetConfigOptionTypeReply
		'''
		
		contextID = self.spec._validateType('ContextID', contextID)
		optionID = self.spec._validateType('string', optionID)
		token = self.asyncGetConfigOptionType(contextID, optionID, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.GetConfigOptionTypeReply(reply)
	
	class GetConfigOptionTypeReply(object):
		'''
		Class containing a reply from 'syncGetConfigOptionType'
		'''
		
		def __init__(self, args):
			self.values = args
			self.type = args[1]
		def __repr__(self):
			return str(self.values)
	
	def asyncGetSupportedConfigOptions(self, contextID, done = None, progress = None):
		'''
		Get the list of #connect option IDs.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@param done	Callback to invoke once command completes
		@type done: DoneGetSupportedConfigOptions
		@param progress	Callback to invoke if command issues progresss
		@type progress: ProgressListener
		@return Command
		'''
		
		if not contextID: contextID = None
		if not done: done = self.__class__.DoneGetSupportedConfigOptions()
		contextID = self.spec._validateType('ContextID', contextID)
		command = self.service.sendCommand('getSupportedConfigOptions', [contextID], done)
		if progress: command.setProgressListener(progress)
		return command
	
	class DoneGetSupportedConfigOptions(Studio.agent.Callback):
		'''
		Callback class for completion of 'asyncGetSupportedConfigOptions'
		'''
		
		def __init__(self):
			self.command = None
		def done(self, error, args):
			if error: self.onError(error)
			else: self.onReply(*args)
		def onError(self, error):
			raise Studio.agent.CommandException(error, self.command)
		def onReply(self, error, optionIDs):
			if error: raise Studio.agent.CommandException(error, self.command)
	
	def syncGetSupportedConfigOptions(self, contextID, progress = None, timeout = Studio.agent.defaultTimeout):
		'''
		Get the list of #connect option IDs.
		@param contextID	
		@type contextID: Studio.agent.Context or context ID
		@return GetSupportedConfigOptionsReply
		'''
		
		contextID = self.spec._validateType('ContextID', contextID)
		token = self.asyncGetSupportedConfigOptions(contextID, None, progress)
		reply = token.awaitReply(timeout)
		return self.__class__.GetSupportedConfigOptionsReply(reply)
	
	class GetSupportedConfigOptionsReply(object):
		'''
		Class containing a reply from 'syncGetSupportedConfigOptions'
		'''
		
		def __init__(self, args):
			self.values = args
			self.optionIDs = args[1]
		def __repr__(self):
			return str(self.values)
	
	