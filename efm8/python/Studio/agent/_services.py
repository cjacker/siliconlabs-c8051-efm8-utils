
import Studio.agent

class WrappedService(Studio.agent.Service):
    '''
    This class wraps a given TCF service with all its commands and event handlers.
    '''
    def __init__(self, tcfService, spec):
        self.tcfService = tcfService
        self.spec = spec
    
    def getSession(self):
        return self.tcfService.session
        
    def sendCommand(self, commandName, arguments, done):
        return self.tcfService.sendCommand(commandName, arguments, done)
    
    def fetchChildren(self, parent):
        return self.tcfService.fetchChildren(parent)
    
    def addListener(self, listener):
        return self.tcfService.addListener(listener)
    
    def removeListener(self, listener):
        return self.tcfService.removeListener(listener)

    
