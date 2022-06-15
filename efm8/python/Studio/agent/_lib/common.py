"""
Common utilities for use by SiAgent Python scripts.

Use "import common" to get these.
"""    
import Studio.agent
import sys, time

DEBUG = False

OPTION_SERIAL_NUMBER = 'serialNumber'
OPTION_ADDRESS = 'address'
OPTION_MCU = 'mcu'
OPTION_KIT = 'kit'

from Studio.agent.services.DeviceSupport import *
from Studio.agent.services.DebugAdapter import *
from Studio.agent.services.RunControl import *


def connect(session, properties, adapter = None, options={}):
    """ Establish a debug session to the given device.  Return the RunControl context and the connected device context """
    debugAdapter = session.getService('DebugAdapter')
    deviceSupport = session.getService('DeviceSupport')
    runControl = session.getService('RunControl')
    
#    awaitRunControl = device and device.Type == TYPE_MCU
    awaitRunControl = True
    
    class RunControlListener(RunControlEventListener):
        def __init__(self):
            self.rcCtx = None
        def onContextAdded(self, contexts):
            self.rcCtx = contexts[0]
            
    rcListener = RunControlListener()
    runControl.addListener(rcListener)

    reply = debugAdapter.syncConnect(properties)
    device = reply.device
    if not OPTION_DEVICE_DESCRIPTOR_PATHS in properties and device and device['Family']:
        jsonPath = Studio.agent.getAgentDirectory() + "/../data/json/default_" + device['Family'].lower() + ".json"
        properties[OPTION_DEVICE_DESCRIPTOR_PATHS] = [jsonPath]
    
    
    if awaitRunControl:
        timeout = time.time() + 5
        while not rcListener.rcCtx:
            time.sleep(0.05)
            if time.time() > timeout:
                raise Studio.agent.TCFException("no RunControlContext reported in 5 seconds")
            
        runControl.removeListener(rcListener)
            
        # the connection may have happened e.g. on the MCU instead of on a kit. 
        
        deviceID = rcListener.rcCtx[PROP_CREATOR_ID]
        if deviceID == device['ID']:
            rcDevice = device
        else:
            rcDevice = runControl.syncGetContext(deviceID).context
            
        return rcListener.rcCtx, rcDevice
    
    else:
        return None, device

def disconnect(session, rcCtx, rcDevice):
    debugAdapter = session.getService('DebugAdapter')
    debugAdapter.syncDisconnect(rcDevice)
    
