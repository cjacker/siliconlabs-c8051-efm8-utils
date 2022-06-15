
"""
This provides interpretation of TCF service specifications (in *.spec files).

A *.spec file describes one TCF service: the names and argument types for commands and replies,
and the kinds of events that will be generated.  

It is a JSON object with these main top-level entries: "name", "url", 
"includes", "types", "consts", "commands", "events".

"name" names the service.
"url" is a pointer to docs.
"includes" is a list of other *.spec files to process (recursive).

The "commands" object is a map of command names to an object with "in"
and "out" argument type lists.

The "events" object is a map of event names to argument type lists.

Argument types are:
    
    "any" -- unspecified (any of the below)
    "object" -- unknown map of names to values
    "string" -- C-style strings
    "integer" -- 32-bit signed ints
    "number" -- typically used for unsigned ints / longs
    "double" -- 64-bit double
    "boolean" -- values "true" / "false"
    "binary" -- raw binary data
    
    "ContextID" : a string which may be passed as a Context object
    "ErrorReport" : a TCF error report object (http://git.eclipse.org/c/tcf/org.eclipse.tcf.git/plain/docs/TCF%20Services.html#ErrorFormat)
    
    or a named type, declared via the "types" entries.

Consts

    A "consts" entry defines a map of name to value pairs.  Fields with the
    given names are available in the wrapped service.
    
Types

    A "types" entry declares a list of types.
    
    Each type is an object that contains a single entry mapping the name to 
    the type definition.  The definition is an object with a "type" field,
    which may be either be "object", "array", or "enum".  
    
    Type definitions follow a subset of JSON schema.
    
    For objects, the "properties" declares a map of names to types.
    For arrays, the "items" declares a map with a "type" field defining the element type.
    For enums, either:
        -- it contains a list of strings, making a enum string definition
        -- it contains a list of maps whose single element maps the 
        constant name to the value sent to TCF.

    Enum constant values are also defined in the target service class.
"""

import Studio.agent
import json
from UserString import UserString
import types, sys, imp

import re, os.path
from encodings.base64_codec import base64_encode

# Paths on which to find *.spec files (set by agent and overridable via "-specs")
_specPaths = []

DEBUG = False

def find(file):
    specFile = None
    for path in _specPaths:
        sp = os.path.join(path, file)
        if os.path.exists(sp):
            return sp
    return None
            
COMMENT_PATTERN = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
COMMA_PATTERN = re.compile(r'(?ms),(\s*[}\]])')
ESCAPED_NEWLINE_PATTERN = re.compile(r'(?ms)\\[ \t]*\r?\n[ \t]+')

def sanitizeJSON(str):
    """ Make the text sanitary for the JSON parser:
    -- remove comments
    -- remove commas before '}' or ']'
    -- combine lines ending in \
    """
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " " # note: a space and not an empty string
        else:
            return s
 
    un = re.sub(COMMENT_PATTERN, replacer, str)
    un = COMMA_PATTERN.sub(r'\1', un)
    un = ESCAPED_NEWLINE_PATTERN.sub(r'', un)
    
    if DEBUG and un != str: print "sanitized:\n",un
    return un


class BaseType(object):
    def __init__(self):
        self.name = "any"
    def __repr__(self):
        return "any"
    def convert(self, argType, argVal):
        return None
    def resolve(self):
        return self
    
class ContextType(BaseType):
    def __init__(self):
        self.name = "Context"
    def __repr__(self):
        return "Studio.agent.Context or property map"
    
    def convert(self, argType, argVal):
        if argVal is Studio.agent._agent._NullArg or not argVal:
            return None
        try:
            return argVal.getProperties()
        except:
            return argVal

class ContextIDType(BaseType):
    def __init__(self):
        self.name = "ContextID"
    def __repr__(self):
        return "Studio.agent.Context or context ID"
    
    def convert(self, argType, argVal):
        if argVal is Studio.agent._agent._NullArg or not argVal:
            return None
        try:
            return argVal["ID"]
        except:
            try:
                return argVal.ID
            except:
                assert str(argVal) == argVal or unicode(argVal) == argVal, "ContextID must be a string, a Context, or a property map with an ID entry"
                return unicode(argVal)

class ObjectType(BaseType):
    def __init__(self):
        self.name = "object"
    def __repr__(self):
        return "dict of names to values"
        
    def convert(self, argType, argVal):
        return argVal or {}


class PrimitiveType(BaseType):
    def __init__(self, name, pytype, default):
        self.name = name
        self.pytype = pytype
        self.default = default
    def __repr__(self):
        return self.name
    def convert(self, argType, argVal):
        if argVal is Studio.agent._agent._NullArg or not argVal:
            return self.default
        return self.pytype(argVal)

class BinaryType(BaseType):
    def __init__(self):
        self.name = "binary"
    def __repr__(self):
        return "binary data"
    def convert(self, argType, argVal):
        if isinstance(argVal, Studio.agent.Binary):
            return argVal
        return Studio.agent.Binary(argVal)

class ArrayType(BaseType):
    def __init__(self, name, elementType):
        assert name
        self.name = name
        self.elementType = elementType
    def __repr__(self):
        return "list of " + str(self.elementType)
    def convert(self, argType, argVal):
        if not argVal:
            return []
        return [self.elementType.resolve().convert(argType, val) for val in argVal]
    
class MapType(BaseType):
    def __init__(self, name, fieldsToTypes):
        assert name
        self.name = name
        self.fieldsToTypes = fieldsToTypes
    def __repr__(self):
        return self.name
    def convert(self, argType, argVal):
        return argVal or {}

class EnumType(BaseType):
    def __init__(self, name, nameValueMap, extensible):
        assert name
        self.name = name
        self.nameValueMap = nameValueMap
        self.extensible = extensible

    def __repr__(self):
        base = ", ".join([repr(name) for name in self.nameValueMap.keys()])
        return "str (one of " + base + (self.extensible and ", or others" or "") + ")"
        
    def convert(self, argType, argVal):
        try:
            return self.nameValueMap[argVal]  # in case a string
        except KeyError, e:
            if argVal is Studio.agent._agent._NullArg or not argVal:
                return 0
            return int(argVal)
        
class EnumStrType(BaseType):
    def __init__(self, name, nameList, extensible):
        assert name
        self.name = name
        self.nameList = nameList
        self.extensible = extensible
        
    def __repr__(self):
        base = ", ".join([repr(name) for name in self.nameList])
        return "str (one of " + base + (self.extensible and ", or others" or "") + ")"
        
    def convert(self, argType, argVal):
        string = str(argVal)
        if not self.extensible and not string in self.nameList:
            raise ValueError("unknown value: " + string + " for " + str(argType))
        return string

class ForwardType(BaseType):
    def __init__(self, specs, name):
        self.specs = specs
        self.name = name
    def __repr__(self):
        return repr(self.specs.findType(self.name))
    def resolve(self):
        resolved = self.specs.findType(self.name)
        if not resolved:
            raise Exception("no type '" + self.name + "' defined")
    
class TypedArgument(object):
    def __init__(self, spec, map):
        keys = list(map.keys())
        self.default = None
        self.defaultExpr = None
        self.required = True
        self.omitted = False
        self.doc = None
        try:
            self.required = map["required"]
            keys.remove("required")
        except KeyError, e:
            pass
        try:
            self.defaultExpr = map["defaultExpr"]
            keys.remove("defaultExpr")
        except KeyError, e:
            pass
        try:
            self.default = map["default"]
            keys.remove("default")
        except KeyError, e:
            pass
        try:
            self.omitted = map["omitted"]
            keys.remove("omitted")
        except KeyError, e:
            pass
        try:
            self.doc = map["$doc"]
            keys.remove("$doc")
        except KeyError, e:
            pass
        
        assert len(keys) == 1
        self.name = keys[0]
        self.typeName = map[self.name]
        
        if not isinstance(self.typeName, str) and not isinstance(self.typeName, unicode):
            print map
            assert False

        self.type = spec._decodeType(self.typeName, self.typeName)
        
class Const(object):
    def __init__(self, name, value, doc):
        self.name = name
        self.value = value
        self.doc = doc
        
class Command(object):
    def __init__(self, name, args, replyInfo, doc):
        self.name = name
        self.args = args
        self.replyInfo = replyInfo
        self.doc = doc
class Event(object):
    def __init__(self, name, args, doc):
        self.name = name
        self.args = args
        self.doc = doc
        
class ServiceSpecification(object):
    def __init__(self):
        self.serviceName = None
        self.consts = []
        self.types = []
        self.commands = []
        self.events = []
        
        self.types.append(PrimitiveType("any", object, dict()))
        self.types.append(ObjectType())
        self.types.append(BinaryType())
        self.types.append(PrimitiveType("integer", int, 0))
        self.types.append(PrimitiveType("double", float, 0.0))
        self.types.append(PrimitiveType("long", long, 0))
        self.types.append(PrimitiveType("number", long, 0))
        self.types.append(PrimitiveType("string", str, None))
        self.types.append(PrimitiveType("boolean", bool, False))
                          
        self.types.append(ContextType())
        self.types.append(ContextIDType())
        
    def __repr__(self):
        return "ServiceSpecification for " + str(self.serviceName)
    
    def findType(self, typeName):
        for type in self.types:
            if type.name == typeName:
                return type
        return None
        
    def _decodeType(self, typeName, info):
        if isinstance(info, str) or isinstance(info, unicode):
            type = self.findType(info)
            if not type:
                return ForwardType(self, info)
            return type
    
        if info["type"] == "object":
            fieldMap = {}
            for name, finfo in info["properties"].iteritems():
                fieldMap[name] = self._decodeType(name, finfo)
            return MapType(typeName, fieldMap)
        elif info["type"] == "array":
            return ArrayType(typeName, self._decodeType(None, info["items"]["type"]))
        elif info["type"] == "enum":
            extensible = info.get("extensible", False)
            try:
                # normal enums: name:value map
                valueMap = {}
                for name, value in info["values"].iteritems():
                    valueMap[name] = value 
                return EnumType(typeName, valueMap, extensible)
            except AttributeError, e:
                # list of values
                nameList = [str(x) for x in info["values"]]
                return EnumStrType(typeName, nameList, extensible)
        else:
            assert False, "expected 'object' or 'array' in " + str(info)

    def _unpackArgs(self, listOfMaps):
        args = []
        gotOptional = False
        for map in listOfMaps:
            typedArg = TypedArgument(self, map)
            args.append(typedArg)
            
        return args 
        
    def loadFrom(self, filename, filelike):
        try:
            text = filelike.read()
            text = sanitizeJSON(text)
            obj = json.loads(text)
        except AttributeError, e:
            obj = json.load(filelike)
        except Exception, e:
            raise Studio.agent.TCFException("could not load " + filename, e)
            
        if "name" in obj:
            assert not self.serviceName, "redefining 'Name' (" + str(self.serviceName) + " with " + obj['name'] + ")"
            self.serviceName = obj["name"]
            self.fileName = filename
        
        if "includes" in obj:
            for include in obj["includes"]:
                sp = find(include)
                if not sp:
                    raise IOException("no include file " + include + " found on " + str(_specPaths))
                file = open(sp, "r")
                with file:
                    self.loadFrom(sp, file)
        
        if "consts" in obj:
            for ent in obj["consts"]:
                keys = list(ent.keys())
                doc = None
                try:
                    doc = ent["$doc"]
                    keys.remove("$doc")
                except KeyError, e:
                    pass
                assert len(keys) == 1
                name, value = keys[0], ent[keys[0]]
                if isinstance(value, unicode):
                    value = str(value)
                self.consts.append(Const(name, repr(value), doc))
            
        if "types" in obj:
            for ent in obj["types"]:
                assert len(ent.items()) == 1
                type, info = ent.items()[0]
                self.types.append(self._decodeType(type, info))
            
        if "commands" in obj:
            for commandName, info in obj["commands"].iteritems():
                try:
                    inArgs = info["in"]
                except:
                    inArgs = []
                try:
                    outArgs = info["out"]
                except:
                    outArgs = []
                    
                try:
                    doc = info["$doc"]
                except:
                    doc = None
                    
                if DEBUG: print "inargs:",inArgs
                commandArgs = self._unpackArgs(inArgs)
                replyArgs = self._unpackArgs(outArgs)
                
                self.commands.append(Command(commandName, commandArgs, replyArgs, doc))
            
        if "events" in obj:
            for eventName, info in obj["events"].iteritems():
                outArgs = info["args"]
                eventArgs = self._unpackArgs(outArgs)
                self.events.append(Event(eventName, eventArgs, info.get("$doc", None)))
            
        
    def _validateType(self, argType, argVal):
        """ Called at runtime (when command/reply/event is handled)
        to make sure the object matches the expected type. """
        type = self.findType(argType)
        if not type:
            if DEBUG: print self.serviceName,"spec types:",self.types.keys()
            raise AssertionError("no such type " + argType)
        
        return type.convert(argType, argVal)
