'''
Script API for SiAgent (TCF) access.

This variant is only used by SiAgent in standalone mode.  It mirrors 
the API used inside Studio, but is implemented in Python.

'''
NAME = str
'''
Name of this module
@value "agent"
'''

VERSION = int
'''
Version of this API
@value (0 << 16) | (0 << 8) | 0
'''

import sys, time, threading, traceback, heapq
import subprocess, re

import Studio
import _channel
import _specs
import _decorate

from Studio.agent import TCFException
from Studio.agent import TimeoutException
from _channel import Message

import os.path

# When enabled, dumps TCF channel and message encoding/decoding traffic (set via "-va")
DEBUG = False 

# When enabled, binary data is transmitted very efficiently instead of BASE64
ZERO_COPY = True

# When set, *.spec files are converted to *.py before loading
GENERATE = False
# When set, *.spec files are dynamically converted to class code
DYNAMIC = False

# default timeout for command handling
defaultTimeout = 5

# map of service to filepath
_generatedClasses = {}

class _NullArg(object):
    pass

class Binary(str):
    def __init__(self, data):
        self.data = data is not _NullArg and data or ""
        if Studio.agent.ZERO_COPY:
            self.json = "(" + str(len(self.data)) + ")" + self.data
        else:
            self.json = base64_encode(self.data)
        #print "*** Binary.toJSON:",self.json
    def __eq__(self, other):
        return isinstance(other, Binary) and self.data == other.data
    def __ne__(self, other):
        return not self.__eq__(other)
    def toJSON(self):
        return self.json
    
class Callback(object):
    '''
    Basic interface for an asynchronous callback from a command sent via
    {@link Service#sendCommand(str, object[], Callback)}.
    '''
    def done(self, error, replyArguments):
        '''
        This method is invoked once a command has finished.
        @param error error object (usually IErrorReport) or None
        @param replyArguments array of reply arguments (the number depends on the command)
        @type error: org_eclipse_tcf_protocol_IErrorReport
        @type replyArguments: list
        '''
        if error:
            raise error
        pass

class ProgressListener(object):
    def handleProgress(self, command, progressArgs):
        ''' Called when a command issues progress.  
        @param command the Command that has progress
        @param progressArgs arguments parsed from the progress message
        '''
        pass
    
class Command(object):
    '''
    This token is the handle to the asynchronous reply from {@link Service#sendCommand(str, object[], Callback)}.
    It may be used to synchronize on the reply via {@link Command#awaitReply()}.
    '''
    def __init__(self, session, msg):
        self.session = session
        self.token = str(msg.token)
        self.msg = msg
        self._progress = None

    def setProgressListener(self, progress):
        ''' Assign a listener for progress messages from the command. '''
        self._progress = progress
    def getProgressListener(self):
        ''' Get the listener for progress messages from the command. '''
        return self._progress
                
    def __repr__(self):
        return "Command [" + self.token+"]" + (self.msg and " " + str(self.msg) or "")

    def awaitReply(self, timeout = 10):
        '''
        Await the reply from the receiver's command.
        @param timeout time to wait in seconds
        @return array of arguments from successful command completion;
        for most commands this consists of an error object and zero or more reply objects
        @throws Exception if reply not received or fails.  NOTE: this does NOT throw
        an exception if the command returned an error; you must check that explicitly.
        '''

        if DEBUG: print "Command.awaitReply",self

        endtime = time.time() + timeout
        while time.time() < endtime:
            if not self.session.isOpen():
                raise TCFException("TCF session is no longer open")
            try:
                replyMsg = self.session._getReply(self.token)
                if replyMsg:
                    return replyMsg
                self.session._messageEvent.wait(1)
            except KeyboardInterrupt, e:
                raise TCFException("Interrupted", e)
                
        self.session._removeCommand(self.msg or self.token)
        raise TimeoutException("timeout waiting for reply to " + str(self))
    
    
class EventListener(object):
    '''
    Basic interface for an asynchronous event report from a service 
    (register via {@link Service#addListener(EventListener)}.
    '''
    def handleEvent(self, service, eventName, arguments):
        '''
        Respond to an event reported on the service
        @param service the service reporting an event
        @param eventName name of the event fired
        @param arguments array of decoded arguments
        @type service: Service
        @type eventName: str
        @type arguments: list
        '''
        pass


class Service(object):
    '''
    This interface represents the script interface of the service requested
    by {@link Session#getService(str)}.
    
    The runtime interface to the service will be populated with the commands available
    to the service (look for corresponding *.spec files).
    '''
    def __init__(self, session, name):
        self.session = session
        self.name = name
    
    def __repr__(self):
        return "Service [" + self.name + "]"
    
    def getSession(self):
        '''
        Get the session that owns the service
        @return session
        '''
        return self.session
        
    def sendCommand(self, commandName, arguments, done):
        '''
        Send an asynchronous command to the service
        @param commandName name of the command
        @param arguments arguments for command, or None for no arguments
        @param done subclass of Callback for reply once command completes
        @type commandName: str
        @type arguments: list
        @type done: Callback
        @return 
        @throws Exception
        '''
        msg = self.session._submitCommand(self.name, commandName, arguments, done)
        try:
            done.command = msg
        except AttributeError, e:
            pass 
        command = Command(self.session, msg)
        self.session._tokensToCommands[msg.token] = command
        if DEBUG: print command
        return command
    
    def fetchChildren(self, parent):
        '''
        Convenience method: synchronously fetch all the children of the given context.
        Invokes the getChildren command.
        @param parent context to query (either an ID or a Context object)
        @type parent: object
        @return non-None array of contexts
        '''

        try:
            id = parent.ID
        except:
            id = parent
            
        kids = _syncGetChildContexts(self.session, _CompletionState(), self.name, [id])        
        return kids
    
    
    def addListener(self, listener):
        '''
        Add a listener for events from this service.
        @param listener
    
        @type listener
        : EventListener
        '''
        self.session._addServiceListener(self.name, listener)
    
    
    def removeListener(self, listener):
        '''
        Remove a listener for events from this service.
        @param listener
    
        @type listener
        : EventListener
        '''
        self.session._removeServiceListener(self.name, listener)

class _MessageThread(threading.Thread):
    def __init__(self, session):
        threading.Thread.__init__(self)
        self.session = session
        
    def run(self):
        while self.session.isOpen():
            time.sleep(0.01)
            with self.session._messageLock:
                try:
                    self.session._processMessages()
                except Exception, e:
                    traceback.print_exc(e)
            

def titleCase(str):
    return str[0].upper() + str[1:]

class Context(object):
    def __init__(self, props):
        assert not isinstance(props, Context)
        self._props = props

    def __eq__(self, other):
        if not isinstance(other, Context):
            return False
        return self.ID == other.ID
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __getattr__(self, id):
        if id == "_props":
            raise AttributeError(id)
        
        try:
            return self._props[id]
        except KeyError, e:
            pass
        
        try:
            title = titleCase(id)
            if title != id:
                return self._props[title]
        except KeyError:
            pass
        
        try:
            upper = id.upper()
            if upper != id:
                return self._props[upper]
        except KeyError, e:
            pass
        
        return None
    
    def __getitem__(self, id):
        return self.__getattr__(id)
    
    def __repr__(self):
        try:
            return self.__class__.__name__ + "(" + self._props["ID"] + ")"
        except:
            return self.__class__.__name__
    
    def getProperty(self, propertyId):
        try:
            return self._props[propertyId]
        except:
            return None
        
    def getProperties(self):
        return self._props

class _CompletionState(object):
    def __init__(self):
        self.completion = threading.Condition()
        self.commands = []
        self.errors = []
        self.contexts = []
        self.counter = 0

class _GetContextDone(Callback):
    def __init__(self, state):
        self.state = state
    
    def done(self, error, args):
        with self.state.completion:
            if error:
                self.state.errors.append(error)
            elif args[0]:
                self.state.errors.append(args[0])
            else:
                self.state.contexts.append(args[1])
            self.state.counter -= 1
            self.state.completion.notify_all()
    
class Session(object):
    '''
    This interface represents the script interface to a connection to the agent. 
    '''
    
    _token = 1
     
    def __init__(self, port=None):
        self.channel = _channel.StreamChannel(port=port)
        
        self.specs = {}
        self.services = {}
        
        # need use synchronization instead of polling here (no event/message loop running)
        timeout = time.time() + 5
        while time.time() < timeout:
            hello = self.channel.receiveMessage()
            if hello:
                self._initialize(hello)
                return
            time.sleep(0.1)
            
        raise TCFException("Failed to receive 'E Locator Hello ...' event (no agent running on port " + \
                        Studio._tcfPort + "?)")
    
    def __repr__(self):
        return "Session " + (self.channel and "connected to " + str(self.channel) or "(disconnected)") 
        
    def _initialize(self, hello):
        if DEBUG: print "Session._initialize with:",hello
        if hello.type != 'E' or hello.token or hello.service != 'Locator' or hello.method != 'Hello':
            raise TCFException("expected E Locator Hello message, got " + str(hello)) 
        self._remoteServices = hello.args[0]
        
        self._eventListeners = {}
        
        # map of tokens to Messages we've sent out which are awaiting replies
        self._pendingDones = {}
        # array of (token, error, replyArgs)
        self._pendingReplies = []

        # remember original Command for each token (for progress, debugging, etc)
        self._tokensToCommands = {}        

        self._messageLock = threading.RLock()
        self._messageEvent = threading.Event(self._messageLock)
        
        self._messageThread = _MessageThread(self)
        self._messageThread.daemon = True
        self._messageThread.start()
        
        services = ZERO_COPY and ["ZeroCopy"] or []
        self.channel.sendMessage(Message.event("Locator", "Hello", services))
        
        self._initialDevicesScanned = False
        
    def isOpen(self):
        '''
        Tell if the agent is connected
        '''
        return self.channel != None
    
    def close(self):
        '''
        Disconnect from the agent and close session
        @throws Exception if the connection is closed
        '''
        if self.channel:
            self.channel.close()
            self.channel = None
            
        if self._messageThread:
            self._messageThread.join()
        
    def getService(self, name):
        '''
        Fetch an interface for the given service.  The service
        will be decorated at runtime with the commands and event
        handlers fetched from a corresponding *.spec file.
        @param name
        @type name: str
        @return service
        @throws Exception
        '''
        if not self._remoteServices:
            raise TCFException("Not connected!") 
        
        service = self.services.get(name, None)
        
        if not service:
            if not name in self._remoteServices:
                raise TCFException("No service '" + name + "' available in " + (" ".join(self._remoteServices)))
            
            service = Service(self, name)
            
            service = self._decorate(service)
            
            self.services[name] = service
            
        return service

    def _decorate(self, service):
        specFile = _specs.find(service.name + ".spec")

        if not specFile:
            if DEBUG: print "No *.spec file found for " + service.name
            return service
        
        spec = _specs.ServiceSpecification()
        file = open(specFile, "r")
        with file:
            spec.loadFrom(specFile, file)
        
        decorator = _decorate.ServiceDecorator(spec)
        
        if not DYNAMIC:
            wrappedClassName = service.name + 'Service'
            wrappedModuleName = 'Studio.agent.services.' + service.name
            if GENERATE and not wrappedModuleName in _generatedClasses:
                # generate class 
                servicePath = os.path.join(os.path.split(Studio.agent.__file__)[0], 
                                        "services",
                                        service.name + ".py")
                
                client = Studio.agent._decorate.SourceCodeClient(specFile, service)
                decorator.decorateClass(client)

                # write into Studio._services
                if DEBUG: print "write to",servicePath,"\n",client
                
                file = open(servicePath, "wt")
                with file:
                    file.write(str(client))
                
            # import the module
            __import__(wrappedModuleName)
            
            # find it
            module = sys.modules[wrappedModuleName]
            
            # fetch the class type
            wrappedClass = module.__dict__[wrappedClassName]
            
            _generatedClasses[wrappedModuleName] = wrappedClass  
        else:
            # make a subclass
            wrappedClass = type('Wrapped' + service.name, (service.__class__, ), {})
            decorator.decorateClass(Studio.agent._decorate.DynamicClassClient(wrappedClass))
            
        wrappedService = wrappedClass(service.session, service.name)
        wrappedService.init(spec, service)
        #print "*** wrapped:",dir(wrappedClass), "\n*** orig:",dir(service)
        return wrappedService
        
            
    def _submitCommand(self, serviceName, commandName, arguments, done):
        arguments = [arg for arg in arguments if arg != _NullArg]
        with self._messageLock:
            msg = Message.command(Session._token, serviceName, commandName, *arguments)
            Session._token += 1
            self._pendingDones[msg.token] = done
            self.channel.sendMessage(msg)
        return msg

    def _removeCommand(self, msgOrToken):
        try:
            token = msgOrToken.token
        except AttributeError, e:
            token = msgOrToken
            
        pendingDone = self._pendingDones.pop(token, False)
        if pendingDone == False:
            # already popped!
            pendingDone = None
#                 raise TCFException("unexpected reply: " + str(msgOrToken))
        else:
            del self._tokensToCommands[token]
        
        return pendingDone
                    
    def _processMessages(self):
        """ 
        Process incoming messages, invoking any event handlers and 
        gathering any message replies received since the last call
        into self._pendingReplies. 
        
        Must be run under _messageLock. 
        """ 
        replies = { }
        while self.channel and self.channel.isOpen():
            try:
                msg = self.channel.receiveMessage()
                if not msg:
                    break
            except TCFException, e:
                # error in communication; fail all the waiting commands
                for token in self._pendingDones.keys():
                    heapq.heappush(self._pendingReplies, (token, e, None))
                self._messageEvent.set()
                
                self.channel.close()
                raise e
                
            if DEBUG: print "Session._processMessages:",msg
            
            if msg.type == 'R':
                # Reply
                
                pendingDone = self._removeCommand(msg.token)
                
                # client may or may not need callback
                if pendingDone:
                    try:
                        pendingDone.done(None, msg.args)
                    except TCFException, e:
                        heapq.heappush(self._pendingReplies, (int(msg.token), e, msg.args))
                        self._messageEvent.set()
                        raise e
                    except Exception, e:
                    	ex = TCFException("command completion failed", e, msg)
                        heapq.heappush(self._pendingReplies, (int(msg.token), ex, msg.args))
                        self._messageEvent.set()
                        traceback.print_exc(ex)
                        raise ex
                    
                # gather the replies we've received
                heapq.heappush(self._pendingReplies, (int(msg.token), None, msg.args))
                self._messageEvent.set()
                
            elif msg.type == 'E':
                # Event
                listeners = self._eventListeners.get(msg.service, [])
                for listener in listeners:
                    listener.handleEvent(msg.service, msg.method, msg.args)
            
            elif msg.type == 'P':
                # Progress
                command = self._tokensToCommands.get(msg.token, None)
                if not command:
                    raise TCFException("unexpected progress: " + str(msg))
                
                progress = command.getProgressListener()
                if progress:
                    progress.handleProgress(command, msg.args)
                    
            elif msg.type == 'N':
                # Error -- rejected command
                pendingDone = self._removeCommand(msg.token)

                error = TCFException("command not defined (for command " + msg.token + ")")
                if pendingDone:
                    try:
                        pendingDone.done(error, None)
                    except TCFException, e:
                        heapq.heappush(self._pendingReplies, (int(msg.token), e, None))
                        raise e
                    except Exception, e:
                        heapq.heappush(self._pendingReplies, (int(msg.token), e, None))
                        traceback.print_exc(e)
                        raise TCFException("command completion failed", e, msg.safe())
                
                # keep replies ordered by token
                heapq.heappush(self._pendingReplies, (int(msg.token), error, None))
                self._messageEvent.set()
                
            elif msg.type == 'F':
                # traffic flow
                pass
            
            else:
                print >>sys.stderr, "Unknown message:",msg
                pass

        
    def _getReply(self, token):
        """ Synchronously await a reply to the given token.
        This ASSUMES the client only synchronously fetches replies,
        and discards any other replies with lower token numbers. 
        """
        
        with self._messageLock:
            self._processMessages()
            while self._pendingReplies:
                ptoken, perror, pargs = self._pendingReplies[0] 
                if ptoken > token:
                    # hmm, already passed
                    raise TCFException("command for " + token + " has already been handled (at " + str(ptoken) +")")
                
                self._pendingReplies = self._pendingReplies[1:]
                if str(ptoken) == token:
                    if perror:
                        raise perror
                    return pargs
                else:
                    #if DEBUG: print "\tdiscarding",ptoken,perror,pargs
                    pass

    def _addServiceListener(self, service, listener):
        list = self._eventListeners.get(service, [])
        if not listener in list:
            list.append(listener)
            self._eventListeners[service] = list 
        
    def _removeServiceListener(self, service, listener):
        list = self._eventListeners.get(service, [])
        if listener in list: list.remove(listener)
        self._eventListeners[service] = list 

    def getServiceNames(self):
        '''
        Get the names of the services available from the agent
        @return non-None array
        @throws Exception
        '''
        if not self._remoteServices:
            raise TCFException("Not connected!") 
        srvs = list(self._remoteServices)
        srvs.sort()
        return srvs

def connect(port=None):
    '''
    Finds or connects to a peer agent matching the default options to find SiAgent
    @return new Session
    @throws Exception
    '''
    return Session(port=port)


def getVersion():
    '''
    Get the version of the API in the form &lt;major&gt;&lt;minor&gt;&lt;bugfix&gt;
    where each component takes up one byte.
    
    A version of 0 (0.0.0) means the API is not finalized and may be changing 
    unpredictably between builds without any required change to this version. 
    
            Major revisions imply API breakage.
    
            Minor revisions imply API additions.
    
            Bugfix revisions imply functional changes to correct undefined or broken behavior.
    
    @return int in the form (major&lt;&lt;16) | (minor&lt;&lt;8) | (bugfix)
    '''
    return 0

def getName():
    '''
    Get the name of the module
    @return 
    '''
    return "agent"


def binaryToString(_object):
    '''
    Utility for JSON decoding: convert binary data to 
    a string with binary data.
    '''
    return str(_object)

def stringToBinary(_str):
    '''
    Utility for JSON encoding: convert a string with binary data to 
    a binary stream.
    '''
    return Binary(_str)

def getAgentDirectory():
    '''
    Get the directory where the agent lives.
    '''
    return Studio._agentDir

def getAgentExecutable():
    '''
    Get the agent's executable path.
    '''
    return Studio._agentExe

############

def _syncGetChildContexts(session, state, serviceName, childIds):
    service = session.getService(serviceName)
                
    with state.completion:
        for id in childIds:
            state.commands.append(service.sendCommand('getChildren', [id], _GetChildrenDone(state, service)))
            state.counter += 1

    while True:
        with state.completion:
            if state.counter == 0:
                break
            state.completion.wait(0.1)
    
    with state.completion:
        if state.errors:
            raise TCFException("problems fetching children", childIds, *state.errors)
        
        return [_wrapContext(serviceName, ctx) for ctx in state.contexts]

class DeviceContext(Context):
    def __init__(self, props):
        Context.__init__(self, props)

class RunControlContext(Context):
    ''' A context from RunControl#getChildren(runControlContextID) '''
    def __init__(self, props):
        Context.__init__(self, props)

class TypedDeviceContext(DeviceContext):
    '''  This interfaces identifies synthetic device contexts constructed
         by ContextTree for the purpose of making kit/MCU navigation
         easier.  
     '''
    def __init__(self, props):
        DeviceContext.__init__(self, props)
class DeviceKitContext(TypedDeviceContext):
    ''' A synthetic context from ContextTree '''
    def __init__(self, kit):
        TypedDeviceContext.__init__(self, kit.getProperties())
        self.kit = kit
        self.MCUs = []
        
class DeviceMCUContext(TypedDeviceContext):
    ''' A synthetic context from ContextTree '''
    def __init__(self, mcu):
        TypedDeviceContext.__init__(self, mcu.getProperties())
        self.kit = None

def _wrapContext(service, props):
    ''' Wrap the bare metal dictionary into the proper Context object. '''
    try:
        # in case this is already a Context
        props = props.getProperties()
    except:
        pass
        
    try:
        service = props["Service"]
    except KeyError:
        pass
    
    id = None
    try:
        id = props["ID"]
    except KeyError:
        pass

    parent = None
    try:            
        parent = props["ParentID"]
    except KeyError:
        pass 

    if DEBUG: print "*** _wrapContext",service,id,parent
    if service == "DeviceSupport":
        return DeviceContext(props)
    elif service == "RunControl":
        return RunControlContext(props)
    else:
        print "*** unwrapped",service,"for",props
        return Context(props) 

def _wrapContexts(service, contexts):
    ''' Wrap the array of bare metal dictionaries into a list of Context objects. '''
    if not contexts:
        return []
    return [_wrapContext(service, context) for context in contexts]

class ContextTree(object):
    ''' This represents the state of the TCF context tree,
     devices (kits/MCUs), and serial ports. '''
    
    def __init__(self):
        self._listeners = []

        # map String to Context
        self._deviceContexts = {}
        
        self._typedDeviceContexts = {}
        self._mcuDeviceContexts = {}
        self._kitDeviceContexts = {}
        
        self._treeDirty = True
        
        # map of String to Context
        self._contextMap = {}
        # map of String to list of Context
        self._childMap = {}
        
    def addListener(self, listener):
        ''' Add listener (null/duplicates ignored) '''
        if listener and not listener in self._listeners:
            self._listeners.append(listener)

    def removeListener(self, listener):
        ''' Remove listener (null/duplicates ignored) '''
        if listener in self._listeners:
            self._listeners.remove(listener)
        
    def handleEvent(self, service, eventName, arguments):
        ''' internal method, do not call '''
        if DEBUG: print "handleEvent",service,eventName,arguments
        
        if "contextAdded" == eventName or "contextChanged" == eventName:
            self._updateContexts(service, arguments[0])
        elif "contextRemoved" == eventName:
            for contextId in arguments[0]:
                self._treeDirty |= self._deviceContexts.pop(contextId, None) != None
            if self._treeDirty:
                self._fireListeners()
                
    def _updateContexts(self, service, contexts):
        if DEBUG: print "*** updating",service,contexts
        changed = False
        for context in contexts:
            context = _wrapContext(service, context)
            changed |= self._addContext(context)

        if changed:
            self._fireListeners()

    def _addContext(self, context):
        id = context.ID
        if not id:
            print "*** blank context",context
            return False

        if isinstance(context, DeviceContext):
            self._deviceContexts[id] = context
            self._treeDirty = True
            return True
        elif context.ID == 'root':
            # ignore here
            pass
        else:
            assert False, "unknown context: " + str(context)
            return False
          
    def attach(self, serviceProvider):
        '''' Attach the receiver to track contextAdded/Removed/Changed events.
        '''
        for serviceName in ["DebugAdapter", "DeviceSupport"]:
            service = serviceProvider.getService(serviceName)
            if service:
                service.addListener(self)
            else:
                print >>sys.stderr, "No service",serviceName
            
    def detach(self, serviceProvider):
        ''' Detach the receiver to track contextAdded/Removed/Changed events.
         '''
        for serviceName in ["DebugAdapter", "DeviceSupport"]:
            service = serviceProvider.getService(serviceName)
            if service:
                service.removeListener(self)
            else:
                print >>sys.stderr, "No service",serviceName

    def getContext(self, contextId):
        ''' Get the current "best" context for the given id.
        This will return an {@link ITypedDeviceContext} or the "regular" Context. 
         @param contextId
        @return context or None '''
        return self.getTypedDeviceContext(contextId) or self.getRawContext(contextId)
    
    def getRawContext(self, contextId):
        ''' Get the current context for the given id.
        This will only return a "regular" Context as fetched directly from a TCF event. 
         @param contextId
         @return context or None
         '''
        return self._contextMap.get(contextId, None)
         
    def getTypedDeviceContext(self, contextId):
        ''' Get the current context for the given device id.
         @param contextId
         @return TypedDeviceContext or None
         ''' 
        self._ensureTree()
        return self._typedDeviceContexts.get(contextId, None)
    
    def getDevices(self):
        ''' Return all device contexts in their raw Context form '''
        return list(self._deviceContexts.values())
        
    def getTypedDevices(self):
        '''  Return the typed device contexts. '''
        self._ensureTree()
        return list(self._typedDeviceContexts.values())

    def getMCUDevices(self):
        '''  Return the DeviceMCUContexts. '''
        self._ensureTree()
        return list(self._mcuDeviceContexts.values())
    
    def getKitDevices(self):
        '''  Return the DeviceKitContexts. '''
        self._ensureTree()
        return list(self._kitDeviceContexts.values())

    def getKitsForParent(self, parentId):
        ''' Get the kits attached to this parent (usually an adapter). '''
        return self._getChildren(parentId, DeviceKitContext)

    def getMCUsForParent(self, parentId):
        ''' Get the MCUs attached to this parent (usually an adapter or a kit). '''
        return self._getChildren(parentId, DeviceMCUContext)
    
    def _getChildren(self, parentId, type):
        self._ensureTree()
        return [ctx for ctx in self._childMap.get(parentId, []) if isinstance(ctx, type)]
    
    def copyFrom(self, other):    
        ''' Copy contents from another tree into the receiver '''
        self.clear()
        self._treeDirty = True
        self._ensureTree()
        
    def clear(self):
        self._treeDirty = True
        self._ensureTree()
        self._fireListeners()
        
    def _fireListeners(self):
        for listener in list(self._listeners):
            listener.contextTreeChanged(self)
            
    def _ensureTree(self):
        ''' Get the generic tree synchronized '''
        if not self._treeDirty:
            return
        
        self._childMap.clear()
        self._contextMap.clear()
        
        self._typedDeviceContexts.clear()
        self._kitDeviceContexts.clear()
        self._mcuDeviceContexts.clear()
        
        for ctx in self._deviceContexts.values():
            self._contextMap[ctx.ID] = ctx
            
            dev = ctx
            
            # make a typed context if possible
            type = dev.Type
            if DEBUG: print "*** type=",type
            if "kit" == type:
                # a kit containing MCUs
                kit = self._kitDeviceContexts.get(dev.ID, None)
                if not kit:
                    kit = DeviceKitContext(dev)
                    self._kitDeviceContexts[dev.ID] = kit
                    self._typedDeviceContexts[dev.ID] = kit
            elif "MCU" == type:
                mcu = self._mcuDeviceContexts.get(dev.ID, None);
                if not mcu:
                    mcu = DeviceMCUContext(dev)
                    self._mcuDeviceContexts[dev.ID] = mcu
                    self._typedDeviceContexts[dev.ID] = mcu
                mcu.kit = self._kitDeviceContexts.get(dev.ParentID, None)
            else:
                print >>sys.stderr, "*** device is neither kit nor MCU:", dev
            
        # update kits with MCUs
        for kit in self._kitDeviceContexts.values():
            self._updateKit(kit)
        
        for context in self._contextMap.values():
            parentID = context.ParentID
            self._childMap.get(parentID, []).append(context)
        
        self._treeDirty = False

    def _updateKit(self, kit):
        ''' Make sure a kit points to all its MCUs '''
        mcus = []
        for mcuCtx in self._mcuDeviceContexts.values():
            if mcuCtx.ParentID == kit.ID:
                mcuCtx.kit = kit
                mcus.append(mcuCtx)
        kit.MCUs = mcus
        
class DeviceMemento():
    def __init__(self, device):
        self.hostName = None
        self.address = None
        self.adapterType = None
        self.adapterSerialNumber = None
        self.adapterID = None
        self.adapterName = None
        self.indetermineate = False
        self.locked = False
        self.connected = False
        self.kitFamily = None
        self.kitName = None
        self.kitID = None
        self.mcuFamily = None
        self.mcuName = None
        self.local = True
        
        self.label = None

        if device.kit:
            self.kitName = device.kit.Name
            self.kitFamily = device.kit.Family
            self.adapterId = device.kit.ParentID
            self.kitID = device.kit.KitID
        
        if device.MCU:
            self.mcuName = device.MCU.Name
            self.mcuFamily = device.MCU.Family
            self.indeterminate = device.MCU.Indeterminate
            self.locked = device.MCU.Locked
            self.connected = device.MCU.Connected
        
                                                               
            
    def getLabel(self):
        if not self.label:
            return self._getDefaultLabel()
        
        return self.label

    def _getDefaultLabel(self):
        baseLabel = None
        
        # the adapter name is useful if it is not related to its ID
        meaningfulAdapterName = self.adapterName\
                and not (self.adapterID and self.adapterName in self.adapterID)
                
        if meaningfulAdapterName:
            baseLabel = self.adapterName
        elif self.kitName:
            baseLabel = self.kitName
        elif self.mcuName:
            baseLabel = self.mcuName
            
        else:
            # show remote info if known
            if self.hostName:
                baseLabel = self.hostName
            elif self.address:
                baseLabel = self.address
            elif self.adapterSerialNumber:
                baseLabel = self.adapterSerialNumber
            else:
                baseLabel = "Unnamed"
            
        # append remote info if known and unique
        hostInfo = None
        if self.hostName and baseLabel != self.hostName:
            hostInfo = self.hostName
        elif self.address and baseLabel != self.address:
            hostInfo = self.address
            
        if hostInfo:
            return baseLabel + " on " + hostInfo
        
        # append serial number if informative
        if self.adapterSerialNumber:
            return baseLabel + " (" + self.adapterSerialNumber + ")"
        
        return baseLabel
    
    def setLabel(self, label):
        self.label = label

class Device():
    
    def __init__(self, kit, mcu):
        self.kit = kit
        self.MCU = mcu
        self._memento = None
        
    def __repr__(self):
        return (self.getMemento().getLabel() or "")
    
    def getMemento(self):
        if not self._memento:
            self._memento = DeviceMemento(self)
        return self._memento
    
    def getId(self):
        if self.MCU:
            return "context@" + self.MCU.ID
        if self.kit:
            return "context@" + self.kit.ID
        return None
    
    def __eq__(self, other):
        ''' Tells whether the same number of TCF contexts are present
         and whether their ids match. '''
        if self is other:
            return True
        if not isinstance(other, Device):
            return False
        my = self.getContexts()
        ot = other.getContexts()
        return my == ot

    def __ne__(self, other):
        return not self.__eq__(other)
        
    def improvesOn(self, other):
        ''' Tell whether the receiver has an equivalent set of parent
         contexts and specifies contexts that are None in "other". 
         \n\
         This explicitly excludes equivalency. '''
        if not isinstance(other, Device):
            return False
        
        if not self.kit and other.kit: 
            return False
        if self.kit and not other.kit: 
            return True
        if self.kit and self.kit.ID != other.kit.ID:
            return False

        if not self.MCU and other.MCU:        
            return False
        if self.MCU and not other.MCU:
            return True
        
        # either equivalent or not -- but not an improvement
        return False
        

    def getContexts(self):
        ''' Get all the contexts representing the detectable. 
        @return list of Context '''
        return [ctx for ctx in [self.getKit(), self.getMCU()] if ctx]
    
    def getKit(self):
        ''' Get the kit device context 
        @return Context or None '''
        return self.kit
        
    def getMCU(self):
        ''' Get the MCU device context 
        @return Context or None '''
        return self.MCU


class ConnectionEvent(object):
    ADDED = 'ADDED'
    REMOVED = 'REMOVED'
    CHANGED = 'CHANGED'
    IMPROVED = 'IMPROVED'

def getRunningAgents(includeSelf=False):
    """ Return a list of running agents """
    
    agentExe = getAgentExecutable()
    
    listCommand = [agentExe, '-list']
    
    # see what's currently out there
    infoDump = subprocess.check_output(listCommand, shell=True) 
    runningList = re.split('\r?\n', infoDump)
    
    assert runningList[0].startswith('Format=')
    
    infos = []
    for running in runningList[1:]:
        info = {}
        
        while running:
            m = re.search(r'([A-Za-z]+)=(.+?)(?=$|\s+\S+=.*)', running)
            if m:
                key, val = m.group(1), m.group(2)
                if key == 'Port':
                    val = int(val)
                    if not includeSelf and val == Studio._tcfPort:
                        info = {}
                        break
                elif key == 'PID':
                    val = int(val)
                info[key] = val
                
                running = running[m.end():]
            else:
                break
            
        if info:
            infos.append(info)
        
    return infos
            

def launchAgent(timeout=10):
    """ Launch a new instance of SiAgent, returning the (pid, port) info.
    @param timeout seconds """
    
    # see what's currently out there 
    wasRunningList = getRunningAgents()
    
    # launch our new one
    agentExe = getAgentExecutable()
    popen = subprocess.Popen([agentExe])
    
    # wait for that one's info to appear
    endTime = time.time() + timeout
    newPort = None
    while not newPort:
        if time.time() >= endTime:
            raise Exception("No new siagent process found before timeout")
        time.sleep(0.25)
        runningList = getRunningAgents()
        if runningList == wasRunningList:
            continue
        for running in [r for r in runningList if not r in wasRunningList]:
            newPort = running['Port']
            
    print "*** new agent on port",newPort
    return (popen, newPort)
