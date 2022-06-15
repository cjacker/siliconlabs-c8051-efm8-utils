
"""
This provides script wrapping for TCF services, given a *.spec file.

A *.spec file describes one TCF service: the names and argument types for commands and replies,
and the kinds of events that will be generated.  

It is a JSON object with these main top-level entries: "name", "commands", "events", 
along with "struct" and "array" entries.

The "commands" object is a map of command names to an object with "in"
and "out" argument type lists.

The "events" object is a map of event names to argument type lists.

Argument types are:

"string"
"integer"
"double"
"number"
"boolean"

"ContextID" : a string which may be passed as a Context object
"ErrorReport" : a TCF error report object (http://git.eclipse.org/c/tcf/org.eclipse.tcf.git/plain/docs/TCF%20Services.html#ErrorFormat)

or a named type, declared via the "types" entries.

A "types" entry declares list of  a "name" (string) and a "fields" (map of names to types).  
An "array" entry declares a "name" (string) and an "elementType" (type).  
"""

import Studio.agent
from _specs import *
import json
from UserString import UserString
import types, sys, imp

DEBUG = True

def titleCase(str):
    return str[0].upper() + str[1:]

def _indent(content, count=1):
    lines = content.split('\n')
    indentStr = '\t' * count
    return '\n'.join([indentStr + line for line in lines])
 
def _docstr( doc):
    return "'''\n" + doc + "\n'''\n"

def _methodDoc(doc, argInfo, ret=None):
    fullDoc = doc or ''
    if argInfo:
        for arg in argInfo:
            argDoc = arg.doc or ""
            typeName = str(arg.type)
            fullDoc += '\n@param ' + arg.name + '\t' + argDoc
            fullDoc += '\n@type ' + arg.name + ': ' + typeName
        if ret:
            fullDoc += '\n@return ' + ret
    return fullDoc
    
class DecoratorClient(object):
    """ Implement this class for ServiceDecorator#decorateClass """
    def addAttribute(self, name, content, doc=None):
        raise NotImplementedException
    def addMethod(self, name, content, doc=None):
        raise NotImplementedException
    def addClass(self, name, content, doc=None):
        raise NotImplementedException
    def addModuleClass(self, name, content, doc=None):
        raise NotImplementedException
    
class _SynthArgument(object):
    def __init__(self, name, doc, type):
        self.name = name
        self.doc = doc
        self.type = type
        

class ServiceDecorator(object):
    def __init__(self, spec):
        self.spec = spec
        
    def decorateClass(self, client):
        """ Add content to the client (a DecoratorClient) 
        so *.spec files can be converted to Python code.
        
        Each command will be converted into two methods:
        
            syncCommand(...)  (named from "command", capitalizing the first letter)
                -- This takes the arguments described in the schema and validates them
                against the type information.
                -- It waits for a reply, then returning the reply arguments decoded
                as per the schema, placed into a class <Command>Reply.
                -- If the return args include an ErrorReport, and that error report
                is not empty, throws CommandException with the error.
                -- If the command fails otherwise, throws the TCFException from that.

            asyncCommand(..., Done)  (capitalizing the first 'command' letter)
                -- This takes the arguments described in the schema and validates them
                against the type information.
                -- The "Done" argument is an implementation of the "DoneCommand"
                inner class (see next) (capitalizing the first 'command' letter)
                -- It returns a token, which may be waited via Command#awaitReply.
                -- If the return args include an ErrorReport, and that error report
                is not empty, throws TCFException() with the error.
                -- Otherwise, if the command fails, throws the TCFException from that.
        
        Each command will inject a DoneCommand class:
            -- implements Studio.agent.Callback
            -- for use in the asyncCommand()'s "Done" argument
            -- named by capitalizing the first 'command' letter
            -- provides an onReply(...) method, which takes the names and types of
            arguments in the schema (including an error report, if any)
            -- provides an onError(...) method, which takes either a TCFException
            or CommandException (for any "ErrorReport" reply argument).
            
        For each event:
            on<EventName>(...) (named from "eventName", capitalizing the first letter)
                -- The targeted class automatically adds itself as a listener
                -- Arguments for the event match those in the schema. 
        
        For types that represent enums, their constants are also added. 
         
         Before the wrapped class can be used, the method 
        init(spec, service) must be called, to record the spec, unwrapped
        service, and to add an EventListener to dispatch events.        """
        
        self._addMethod(client, "__repr__",
                            self._generateRepr())
        
        #setattr(classObj, "_spec", self.spec)
        
        self._addModuleClass(client, self.spec.serviceName + "EventListener", 
                        self._generateEventListener())
        self._addMethod(client, "init",
                            self._generateInit())

        for typeObj in self.spec.types:
            name  = typeObj.name
            if isinstance(typeObj, EnumType):
                self._decorateEnums(client, typeObj.nameValueMap)
                
            elif isinstance(typeObj, EnumStrType):
                map = {}
                
                def convert(name):
                    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
                    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
                for name in typeObj.nameList:
                    enumName = convert(typeObj.name + name[0].upper() + name[1:]).upper()
                    map[enumName] = "'" + name + "'"
                self._decorateEnums(client, map)
            elif isinstance(typeObj, MapType):
                self._decorateMappingType(client, name, typeObj.fieldsToTypes)
                
        for const in self.spec.consts:
            client.addAttribute(const.name, const.value, const.doc)
                
        for command in self.spec.commands:
            commandName = command.name
            argInfo = command.args
            replyInfo = command.replyInfo
            
            asyncCommandName = "async" + titleCase(commandName)
            doneCommandName = "Done" + titleCase(commandName)
            syncCommandName = "sync" + titleCase(commandName)
            replyClassName = titleCase(commandName) + "Reply"
            
            aargs = list(argInfo)
            aargs.append(_SynthArgument('done', 
                                       'Callback to invoke once command completes', 
                                       doneCommandName))
            aargs.append(_SynthArgument('progress', 
                                       'Callback to invoke if command issues progresss', 
                                       'ProgressListener'))
            self._addMethod(client, asyncCommandName, 
                            self._generateAsyncCommand(commandName, argInfo),
                            _methodDoc(command.doc, aargs, 'Command'))

            self._addClass(client, doneCommandName, 
                            self._generateDoneCommand(commandName, 
                                                      replyInfo),
                           "Callback class for completion of '" + asyncCommandName + "'")

            aargs = list(argInfo)
            aargs.append(_SynthArgument('timeout', 
                                       'Timeout in seconds to await reply', 
                                       'int'))
            aargs.append(_SynthArgument('progress', 
                                       'Callback to invoke if command issues progresss', 
                                       'ProgressListener'))

            self._addMethod(client, syncCommandName, 
                            self._generateSyncCommand(commandName, asyncCommandName, argInfo, replyInfo),
                            _methodDoc(command.doc, argInfo, replyClassName))

            self._addClass(client, replyClassName, 
                            self._generateReplyClass(replyInfo),
                            "Class containing a reply from '" + syncCommandName + "'")

    def _addMethod(self, client, methodName, code, doc = None):
        
        code = code.replace("$METHOD",methodName)
        
        client.addMethod(methodName, code, doc)
        
    def _addClass(self, client, className, code, doc = None, locs=dict(), globs=dict()):
        
        code = code.replace("$CLASS", className)
        
        client.addClass(className, code, doc)
        
    def _addModuleClass(self, client, className, code, doc = None, locs=dict(), globs=dict()):
        
        code = code.replace("$CLASS", className)
        
        client.addModuleClass(className, code, doc)
        
    def _generateRepr(self):
        code = "def $METHOD(self):\n" + \
                "\treturn '[Service ' + self.service.name + ' with ' + str(self.spec.fileName) + ']'\n"
                
        return code 
    
    def _generateInit(self):
        code = "def $METHOD(self, spec, service):\n" + \
                "\tself.spec = spec\n" + \
                "\tself.service = service\n"
        if self.spec.events:
            code += ("\tself.eventListener = {}EventListener()\n").format(self.spec.serviceName) + \
                    "\tself.service.addListener(self.eventListener)\n"
                
        return code 
    
    def _generateEventListener(self):
        anyEvents = False
        code =  "class $CLASS(Studio.agent.EventListener):\n" + \
                "\tdef handleEvent(self, service, eventName, arguments):\n"

        for event in self.spec.events:
            eventName = event.name
            eventMethodName = "on" + titleCase(eventName)
            
            code += "\t\t{}if eventName == '{}':\n".format(
                           (anyEvents and "el" or ""),
                           eventName)
                     
            # wrap any types
            for arg, idx in zip(event.args, xrange(len(event.args))):
                if arg.typeName == "Context":
                    code += "\t\t\t{0} = Studio.agent._agent._wrapContext({1}, {0})\n".format(
                        'arguments[' + str(idx) + ']',
                        repr(self.spec.serviceName))
                elif arg.typeName == "ContextArray":
                    code += "\t\t\t{0} = Studio.agent._agent._wrapContexts({1}, {0})\n".format(
                        'arguments[' + str(idx) + ']',
                        repr(self.spec.serviceName))

            code += ("\t\t\tself.{}(*arguments)\n").format(eventMethodName)

            anyEvents = True
        
        if anyEvents:
            code += "\t\telse: print 'Unhandled event:', service, eventName, arguments\n"
        else:
            code += "\t\tpass\n"

        for event in self.spec.events:
            eventName = event.name
            eventMethodName = "on" + titleCase(eventName)
            
            doc = 'Callback for event \'' + eventName + '\'.\n'
            if event.doc:
                 doc += '\n' + event.doc 
            fullDoc = _indent(_docstr(_methodDoc(doc, event.args)), 2)
            proto = ', '.join(self._generatePrototype(event.args))
            code += ("\tdef {}(self, {}):\n" + \
                     fullDoc + '\n').format(
                           eventMethodName, proto)
                
            code += "\t\tpass\n"
                
        return code 
    
    def _generateTypeValidation(self, argName, argTypeName):
        code = "\t{} = self.spec._validateType('{}', {})\n".format(
                   argName, argTypeName, argName)
        #code += "\tprint '{}:', type({}), {}\n".format(argName, argName, argName)
        return code 

    def _decorateEnums(self, client, nameToValueMap):
        """ Create enums into the body of a class. """
        # sort by enum
        items = list(nameToValueMap.iteritems())
        items.sort(cmp=lambda x,y: cmp(x[1], y[1]))
        
        for name, value in items:
            #setattr(classObj, name, value)
            client.addAttribute(name, value, None)
    
    def _decorateMappingType(self, client, typeName, fieldsToTypes):
        """ Create a class allowing easy creation of map-based arguments. """
        # sort by enum
        keys = list(fieldsToTypes.keys())
        keys.sort()
        
        code = "class $CLASS(UserDict):\n"
        code += "\tdef __init__(self, "
        
        args = []
        for key in keys:
            args.append(key +"=None")
        code += ", ".join(args)
        
        code += "):\n"
        code += "\t\tUserDict.__init__(self)\n"

        for key in keys:
            code += "\t\tif {}: self['{}'] = {}\n".format(key, key, key)
        
        self._addClass(client, typeName, code)
    
    def _generatePrototype(self, argInfo):
        args = []
        hadOptional = False
        for arg in argInfo:
            name = arg.name
            if arg.omitted:
                continue
            if arg.default:
                name += " = " + str(arg.default)
                hadOptional = True
            elif not arg.required or hadOptional:
                name += " = Studio.agent._agent._NullArg"
                hadOptional = True
            args.append(name)
        return args

    def _generateAsyncCommand(self, commandName, argInfo):
        code = "def $METHOD(self, "
        protoArgs = self._generatePrototype(argInfo)
        protoArgs.append("done = None")
        protoArgs.append("progress = None")
        code += ", ".join(protoArgs) + "):\n"
        
        args = []
        for arg in argInfo:
            if arg.omitted:
                code += "\t{} = {}\n".format(arg.name, arg.defaultExpr)
            else:
                code += "\tif not {}: {} = {}\n".format(arg.name, arg.name, arg.defaultExpr)
            args.append(arg.name)
            
        code += "\tif not done: done = self.__class__.Done" + titleCase(commandName) + "()\n"
        for arg in argInfo:
            if not arg.omitted:
                code += self._generateTypeValidation(arg.name, arg.typeName) 
            
        code += "\tcommand = self.service.sendCommand('{}', [{}], done)\n".format(
                         commandName, 
                         ", ".join(args))
        
        code += "\tif progress: command.setProgressListener(progress)\n"
        code += "\treturn command\n"
        
        return code
    
    def _generateSyncCommand(self, commandName, asyncCommandName, argInfo, replyInfo):
        code = "def $METHOD(self, "
        protoArgs = self._generatePrototype(argInfo)
        protoArgs.append("progress = None")
        protoArgs.append("timeout = Studio.agent.defaultTimeout")
        argStr = ", ".join(protoArgs)
        code += argStr
        code += "):\n"
        
        args = []
        for arg in argInfo:
            if not arg.omitted:
                code += self._generateTypeValidation(arg.name, arg.typeName)
                args.append(arg.name) 
        
        code += "\ttoken = self.{}({}{}None, progress)\n".format(
                         asyncCommandName, ", ".join(args), args and ", " or "")
        
        code += "\treply = token.awaitReply(timeout)\n"
        code += "\treturn self.__class__.{}Reply(reply)\n".format(titleCase(commandName))
        return code

    def _generateReplyClass(self, replyInfo):
        code = "class $CLASS(object):\n" + \
            "\tdef __init__(self, args):\n"
            
        code += "\t\tself.values = args\n"
        
        for ret, idx in zip(replyInfo, xrange(len(replyInfo))):
            if ret.typeName == "ErrorReport":
                # ignore
                pass
            elif ret.typeName == "Context":
                code += "\t\tself.{0} = Studio.agent._agent._wrapContext({1}, args[{2}])\n".format(
                    ret.name, repr(self.spec.serviceName), idx)
            elif ret.typeName == "ContextArray":
                code += "\t\tself.{0} = Studio.agent._agent._wrapContexts({1}, args[{2}])\n".format(
                    ret.name, repr(self.spec.serviceName), idx)
            else:
                code += "\t\tself.{} = args[{}]\n".format(ret.name, idx)

        code += "\tdef __repr__(self):\n" + \
                "\t\treturn str(self.values)\n"
            
        return code

    def _generateDoneCommand(self, commandName, replyInfo):
        code = "class $CLASS(Studio.agent.Callback):\n"
       
        code += "\tdef __init__(self):\n"
        code += "\t\tself.command = None\n"
        
        code += "\tdef done(self, error, args):\n"
        code += "\t\tif error: self.onError(error)\n"
        code += "\t\telse: self.onReply(*args)\n"

        code += "\tdef onError(self, error):\n"
        code += "\t\traise Studio.agent.CommandException(error, self.command)\n"
        
        code += "\tdef onReply(self, "
        args = [arg.name for arg in replyInfo]
        argStr = ", ".join(args)
        code += argStr + "):\n"
        
        anyContent = False
        
        # convert values to wrapped types 
        idx = 0
        for arg in replyInfo:
            if arg.typeName == "ErrorReport":
                anyContent = True
                code += "\t\tif {}: raise Studio.agent.CommandException({}, self.command)\n".format(arg.name, arg.name)
            elif arg.typeName == "ContextID":
                anyContent = True
                code += "\t\tif {}: {} = Studio.agent._agent._wrapContext({}, {})\n".format(
                    arg.name, arg.name, repr(self.spec.serviceName), arg.name)
        if not anyContent:
            code += "\t\tpass\n"
        return code

    def _generateEventHandler(self, eventName, argInfo):
        code = "def $METHOD(self, "
        args = [arg.name for arg in argInfo]
        argStr = ", ".join(args)
        code += argStr + "):\n"
        
        code += "\tpass\n"
        return code


# name that shows up in generated sources
SOURCE_NAME = '<wrapped>'
class DynamicClassClient(DecoratorClient):
    """ Dynamically add attributes/methods to a wrapped service class. """    
    def __init__(self, classObj, moduleObj):
        self.classObj = classObj
        self.moduleObj = moduleObj
    
    def addAttribute(self, name, content, doc):
        setattr(self.moduleObj, name, content)

    def addMethod(self, name, content, doc, argInfo=[]):
        if DEBUG: print "method",name,"is\n",content
        codeObj = compile("from Studio.agent.services import *\n" + content, SOURCE_NAME, 'exec')
         
        locs = dict()
        globs = dict()
        
        exec "import Studio\n" in locs, globs
        
        eval(codeObj, globs, locs)
        setattr(self.classObj, name, locs[name])

    def _addClass(self, target, name, content, doc):
        if DEBUG: print "class",name,"is\n",content
        codeObj = compile("import Studio.agent\n" + content, SOURCE_NAME, 'exec')
         
        locs = dict()
        globs = dict()
        
        exec "import Studio\nfrom UserDict import UserDict" in locs, globs
        
        eval(codeObj, globs, locs)
         
        newClass = locs[name]
        setattr(target, name, newClass)

    def addClass(self, name, content, doc):
        return self._addClass(self.classObj, name, content, doc)
    
    def addClass(self, name, content, doc):
        return self._addClass(self.classObj.__module__, name, content, doc)
    

class SourceCodeClient(DecoratorClient):
    """ Generate source code for a wrapped service class. """    
    
    def __init__(self, specFile, service):
        self.header = '# Auto-generated content -- do not edit!\n'+ \
                    '# If changes needed, edit {} instead, then run siagent with "-generate".\n\n'.format(
                    os.path.split(specFile)[1])
        self.header += 'from Studio.agent.services import *\n'
        self.header += 'import Studio.agent\n'
        self.header += 'from UserDict import UserDict\n'
        self.header += '\n'
        self.classHeader = 'class {}(Studio.agent.Service):\n'.format(service.name + 'Service')
        self.text = ''
        
    def __repr__(self):
        return self.header + self.classHeader + _indent(self.text)
   
    def addAttribute(self, name, content, doc):
        if doc:
            self.header += _docstr(doc)
        if str(content) == content or unicode(content) == content:
            # a string
            if content[0] != "'" and content[0] != '"':
                content = repr(content)
        self.header += '{} = {}\n'.format(name, content)
        self.header += '\n'

    def _appendWithComment(self, text, content, doc):
        if doc:
            pieces = content.split('\n', 1)
            text += pieces[0]
            text += '\n' + _indent(_docstr(doc)) + '\n'
            text += pieces[1]
        else:
            text += content
        return text
    
    def addMethod(self, name, content, doc):
        self.text = self._appendWithComment(self.text, content, doc)
        self.text += '\n'
        
    def addClass(self, name, content, doc):
        self.text = self._appendWithComment(self.text, content, doc)
        self.text += '\n'
        
    def addModuleClass(self, name, content, doc):
        self.header = self._appendWithComment(self.header, content, doc)
        self.header += '\n'
