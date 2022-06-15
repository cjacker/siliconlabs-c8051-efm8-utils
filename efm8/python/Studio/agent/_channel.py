import socket

import json, json.encoder, json.decoder, time

try:
	from cStringIO import StringIO
except:
	from StringIO import StringIO

import UserDict

import Studio
from Studio.agent import TCFException

# if set, debug low-level channel traffic (-vc)
DEBUG = False		

# maximum message chunk read/processed at once
BUFSIZE = 4096		

ESC = '\003'

class TCFJsonEncoder(json.encoder.JSONEncoder):
	def default(self, o):
		try:
			return json.encoder.JSONEncoder.default(self, o)
		except TypeError, e:
			return o.toJSON()
		
_HEX= "0123456789ABCDEF"
def _hexbyt(b):
	return _HEX[(b>>4)&0xf] + _HEX[b&0xf]

def tohex(data):
	if isinstance(data, Studio.agent.Binary):
		data = str(data.data)
		
	if len(data) < 80:
		return (" ".join([_hexbyt(ord(ch)) for ch in data]))
	
	lines = []
	step = 20
	for i in xrange(0, len(data), step):
		hexdump = (" ".join([_hexbyt(ord(ch)) for ch in data[i:i+step]]))
		asciidump = ("".join([(ord(ch) < 32 or ord(ch) > 126) and '.' or ch for ch in data[i:i+step]]))
		lines += [str(i) + ": " + hexdump+ " " + asciidump]
	return "\n".join(lines)

class Event(object):
	def __init__(self, type, token, service, method, args):
		self.type = type
		self.token = token
		self.method = method
		self.service = service
		self.args = args
		
	def __repr__(self):
		return self.type + ' ' + \
			(self.token and str(self.token) + ' ' or '') + \
			self.service + ' ' + \
			(self.method and str(self.method) + ' ' or '') + \
			 " ".join([str(arg) for arg in self.args])


class Message(object):
	@staticmethod
	def fromStream(streamData):
		""" Decode a TCF message in its standard form
		(\000 between tokens, two \000 at end)
		"""
		
		i = prev = 0
		pieces = []
				
		while i < len(streamData):
			#if DEBUG: print "parsing",i,"=",streamData[i]
			if streamData[i] == '\000':
				pieces.append(streamData[prev:i])
				i += 1
				prev = i
			elif i == prev:
				if streamData[i] == '(':
					if DEBUG: print "JSON binary at",i
					# json binary
					idx = streamData.find(')', i+1)
					if idx < 0:
						raise TCFException("unknown binary data in " + streamData + " (" + tohex(streamData) + ")")
					#pieces.append(streamData[i+1:idx])
					length = int(streamData[i+1:idx])
					if DEBUG: print "len:",length
					prev = idx + 1
					end = prev + length
					pieces.append(Studio.agent.Binary(streamData[prev:end]))
					prev = i = end + 1
				else:
					i = streamData.index('\000', i+1)
		
# 		if DEBUG: 		
# 			for piece in pieces:
# 				print "piece:",piece,"==>",tohex(piece)
		
		try:
			type = pieces[0]
			token = service = method = None
			textArgs = None
			if type == 'C':
				token, service, method, textArgs = pieces[1], pieces[2], pieces[3], pieces[4:]
			elif type == 'E':
				service, method, textArgs = pieces[1], pieces[2], pieces[3:]
			elif type == 'R' or type == 'P':
				token, textArgs = pieces[1], pieces[2:]
			elif type == 'N':
				token = pieces[1]
			elif type == 'F':
				token = pieces[1]
			elif type:
				raise TCFException("unexpected message", streamData)
			else:
				# empty
				return None
			
		except IndexError, e:
			raise TCFException(str(e) + " in " + streamData + " (" + tohex(streamData) + ")")
			
		if textArgs:
			args = []
			for textArg in textArgs:
				# json may be blank (for null/None) or actual text
				if not textArg:
					args.append(None)
				elif isinstance(textArg, Studio.agent.Binary):
					args.append(textArg)
				else:
					try:
						val = json.loads(textArg)
					except ValueError, e:
						try:
							val = json.loads(textArg.replace('\r', "\\r").replace('\n', "\\n"))
						except ValueError, e:
							raise TCFException(str(e) + " in " + textArg + " (" + tohex(textArg) + ")")
					args.append(val)
		else:
			args = []
			 
		return Message(type, token, service, method, args)
	
	@staticmethod
	def command(token, service, method, *args):
		return Message('C', token, service, method, args)
		
	@staticmethod
	def event(service, method, *args):
		return Message('E', None, service, method, args)
		
	def __init__(self, type, token, service, method, args):
		self.type = type
		self.token = token and str(token)
		self.service = service
		self.method = method
		self.args = args
		
	def __repr__(self):
		return self.type + ' ' + \
			(self.token and (self.token + ' ') or '') + \
			(self.service and (self.service + ' ') or '') + \
			(self.method and (self.method + ' ') or '') + \
			 " ".join([str(arg) for arg in self.args])
			 
	def toStream(self):
		stream = self.type + '\000'
		if self.token:
			stream += str(self.token) + '\000'
		if self.service:
			stream += self.service + '\000'
		if self.method:
			stream += self.method + '\000'
		for arg in self.args:
			if arg is not None:
				if isinstance(arg, Studio.agent.Binary):
					stream += arg.toJSON()
				else:  
					if isinstance(arg, UserDict.UserDict):
						arg = dict(arg.data)
					stream += json.dumps(arg, separators=(',',':'))
			stream += '\000'
		if DEBUG: print "Message.toStream:",stream.replace('\000', ' '),"==>",tohex(stream)
		return stream

		
class StreamChannel(object):
	""" Send/receive complete messages with a TCP connection.
	
	The TCP TCF protocol encodes a message like:
	
	C 123 Service message 1 "la"
	
	as
	
	'C' \0 '123' \0 'Service' \0 'message' \0 '1' \0 '"la"' <eom>
	
	The end-of-message is:
	
		ESC \001
	
	The end-of-stream is:
	
		ESC \002
	
	A literal \003 is:
	
		ESC \000
	
    TCP channels also wraps big chunks binary-encoded data (sent when the "ZeroCopy" service is reported) as:
    
        \003 \003 <len|0x80> ... <len> <data>
    
        where the length of the data is broken into 7 bit chunks and sent from lowest to highest.
        All the leading bytes except the last are OR'ed with 0x80.
	"""
	def __init__(self, sock=None, address='127.0.0.1', port=None):
		if sock is None and port is None:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.port = int(Studio._tcfPort)
			self.sock.connect((address, self.port))
		elif port:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.port = int(port)
			self.sock.connect((address, self.port))
		else:
			self.sock = sock
			self.port = port
		
		if DEBUG: print "Connected to port",self.port

		self.sock.setblocking(False)

		self.atEOS = False
		
		# list of messages we're waiting to process		
		self.input = []
		self.inputPartial = None
		
	def __repr__(self):
		return "[TCF channel, port " + str(self.port) + "]"
		
	def isOpen(self):
		return self.sock != None
		
	def close(self):
		if self.sock:
			self.sock.setblocking(True)
			self.sock.send(ESC + '\002')
			self.sock.close()
		self.sock = None

	def _send(self, msg):
		""" Send a single properly encoded message """
		if not self.sock:
			raise TCFException("socket connection closed")
		offs = 0
		while offs < len(msg):
			try:
				sent = self.sock.send(msg[offs:])
				offs += sent
			except socket.error, e:
				if e.errno == 10035:
					# not blocking -- just keep trying (I only see this on WinXP with 2 cores)
					time.sleep(0.01)
					continue
				raise TCFException("socket connection broken: " + str(e))

	def _decodeStr(self, str):
		#print "str:",str,tohex(str)
		
		unescaped = str #str.replace(ESC + '\000', '\003')

		return Message.fromStream(unescaped)
		
	def _receive(self):
		""" Read whatever's available and add messages to 'input' """ 
		if self.atEOS or not self.sock:
			return False
			
		try:
			chunk = self.sock.recv(BUFSIZE)
		except socket.error, e:
			# we do not block
			if e.errno == 11 or e.errno == 35 or e.errno == 10035:
				# Linux, OS X, and Win32 codes for "resource temporarily unavailable" / "no data available"
				return False
			else:
				raise e
			
		if DEBUG: print "StreamChannel._receive: recv #",len(chunk),"=",tohex(chunk[:256]),"..."
		
		if chunk == '':
			self.atEOS = True
			raise TCFException("socket connection broken")
		
		if self.inputPartial:
			if DEBUG: print "StreamChannel._receive: partial #",len(self.inputPartial),"=",tohex(self.inputPartial[:256]),"..."
			chunk = self.inputPartial + chunk
			self.inputPartial = None

		self._parse(chunk)				
		return True
	
	def _parse(self, chunk):
		if DEBUG: print "StreamChannel._parse #",len(chunk),"=",tohex(chunk[:256]),"..."
		
		lastMsgPtr = 0
		i = 0
		stream = StringIO()
		
		# this parses messages Pythonically, where we assume
		# a full message is available, and rely on IndexError
		# to determine it's not
		try:
			while i < len(chunk):
				if chunk[i] == ESC:
					if DEBUG: print "StreamChannel._parse: @"+str(i)+":",tohex(chunk[i:i+16]),"..."
					j = i
					ch = chunk[j+1]
					j += 2
					
					if ch == '\001':
						if DEBUG: print "\tEOM"
						# end of message
						if stream.tell():
							message = self._decodeStr(stream.getvalue())
							if DEBUG: print "\tadding:",message
							self.input.append(message)
							stream = StringIO()
							lastMsgPtr = j
						i = j
						continue
					elif ch == '\002':
						if DEBUG: print "\tEOS"
						# end of stream; error may follow
						self.atEOS = True
						i = j
 					elif ch == '\003':
 						# binary block
 						size = 0
 						
 						shift = 0
 						while True:
 							ch = ord(chunk[j])
 							size |=  (ch & 0x7f) << shift
 							j += 1
 							shift += 7
 							if ch < 0x80:
 								break
 						
 						if DEBUG: print "\tBIN ("+str(size)+")"
 						
 						stream.write(chunk[j:j+size])
 						i = j + size
 						
 						if DEBUG: print "\tBIN following:",tohex(chunk[i:i+16]),"..."
					elif ch == '\000':
						if DEBUG: print "\tESC"
						stream.write(ESC)
						i = j
					else:
						if DEBUG: print "\t???",ord(ch)
						raise TCFException("unexpected character after escape: " + str(ord(ch)) + " in " + tohex(stream.getvalue()))
				else:
					# normal char
					stream.write(chunk[i])
					i += 1
					
			if stream.tell():
				self.inputPartial = chunk[lastMsgPtr:]
				if DEBUG: print "\tPARTIAL EXIT ("+str(len(self.inputPartial))+")"
		except IndexError, e:
			if stream.tell():
				self.inputPartial = chunk[lastMsgPtr:]
				if DEBUG: print "\tPARTIAL EXIT ("+str(len(self.inputPartial))+")"
		finally:
			stream.close()
				
	def receiveMessage(self):
		""" Get the next message """
		while self._receive(): 
			pass
		if self.input:
			if DEBUG: print "StreamChannel.receiveMessage: queue size=",len(self.input)
			message, self.input = self.input[0], self.input[1:]
			return message
		return None
		
	def sendMessage(self, msg):
		""" Send a message """
		stream = msg.toStream()
		stream = stream.replace('\003', ESC + '\000') + ESC + '\001'
		if DEBUG: print "StreamChannel.sendMessage:",stream.replace('\000', ' ')
		self._send(stream)
		