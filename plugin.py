# Connect to Homekit Device in Insecure mode
#
# Author: MacJL
#
"""
<plugin key="HomekitInsecureClient" name="Homekit Insecure Client" author="MacJL" version="0.2" wikilink="http://www.domoticz.com/wiki/plugins" externallink="https://github.com/macjl/Domoticz-HomekitInsecureClient">
    <description>
        Control Homekit Devices which are set in insecure mode (eg : Homebridge, HAA, etc...)
    </description>
    <params>
        <param field="Address" label="IP Address of homekit device or bridge" width="200px" required="true" default="127.0.0.1"/>
        <param field="Port" label="PORT of homekit device or bridge" width="50px" required="true" default="54821"/>
        <param field="Password" label="Authorization key" width="80px" required="true" default="031-45-154"/>
    </params>
</plugin>
"""
import Domoticz
import json

class BasePlugin:
    enabled = False
    httpConn = None
    headers = { 'Content-Type': 'Application/json'}
    iid = 0
               

    def __init__(self):
        #self.var = 123
        return

    def onStart(self):
        Domoticz.Log("onStart called")
        Domoticz.Debugging(0)
#        if (len(Devices) == 0):
#            Domoticz.Device(Name="Socket 1", Unit=int(Parameters["Mode1"]), TypeName="Switch").Create()
#            Domoticz.Log("Device created.")
        DumpConfigToLog()
        self.headers = { 'Content-Type': 'Application/json',
                'Authorization': Parameters["Password"]}
        self.iid = Parameters["Mode2"]
        self.httpConn = Domoticz.Connection(Name="Homekit", Transport="TCP/IP", Protocol="HTTP", Address=Parameters["Address"], Port=Parameters["Port"])
        self.httpConn.Connect()

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")
        if (Status == 0):
            Domoticz.Debug("Connection successfull")
            self.httpConn.Send({'Verb':'GET', 'URL':'/accessories', 'Headers': self.headers})
        else:
            Domoticz.Log("Failed to connect ("+str(Status)+") to: "+Parameters["Address"]+":"+Parameters["Port"]+" with error: "+Description)

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")
        DumpHTTPResponseToLog(Data)
        strData = Data["Data"].decode("utf-8", "ignore")
        #Domoticz.Log( strData )
        accessories = json.loads(strData)["accessories"]
        for accessory in accessories:
            hkaid = accessory["aid"]
            supported = 0
            for service in accessory["services"]:
                if( service["type"] == "3E" ):
                    for characteristic in service["characteristics"]:
                        if ( characteristic["type"] == "23" ):
                            hkName = characteristic["value"]
                        if ( characteristic["type"] == "20" ):
                            hkManufacturer = characteristic["value"]
                if( service["type"] == "47" ):
                    for characteristic in service["characteristics"]:
                        if ( characteristic["type"] == "25" ):
                            hkiid = str( characteristic["iid"] )
                            hkValue = characteristic["value"]
                            supported = 1
            if ( supported == 1 and hkManufacturer != "eDomoticz" ):
                Domoticz.Log( hkManufacturer + " - " + hkName + " - " + str( hkaid ) + " - " + hkiid + " - " + str (hkValue) )
                try:
                    Devices[hkaid].Touch
                except:
                    Domoticz.Device(Name=hkName, Unit=hkaid, TypeName="Switch", DeviceID=hkiid).Create()
                    Domoticz.Log("Device created.")
                if ( hkValue == 1 ):
                    Devices[hkaid].Update(nValue=1,sValue="On")
                if ( hkValue == 0 ):
                    Devices[hkaid].Update(nValue=0,sValue="Off")




    def onCommand(self, Unit, Command, Level, Hue):

        if str(Command) == "On":
            Devices[Unit].Update(nValue=1,sValue="On")
            nValue = "1"
        if str(Command) == "Off":
            Devices[Unit].Update(nValue=0,sValue="Off")
            nValue = "0"

        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        data = "{\"characteristics\":[{\"aid\":" + str(Unit) + ",\"iid\":" + self.iid + ",\"value\":" + nValue + "}]}"
        Domoticz.Log(data)
        self.httpConn.Send({'Verb':'PUT', 'URL':'/characteristics', 'Headers': self.headers, 'Data': data})

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")
        self.httpConn.Send({'Verb':'GET', 'URL':'/accessories', 'Headers': self.headers})

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    DumpHTTPResponseToLog(Data)
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

def DumpHTTPResponseToLog(httpResp, level=0):
    if (level==0): Domoticz.Debug("HTTP Details ("+str(len(httpResp))+"):")
    indentStr = ""
    for x in range(level):
        indentStr += "----"
    if isinstance(httpResp, dict):
        for x in httpResp:
            if not isinstance(httpResp[x], dict) and not isinstance(httpResp[x], list):
                Domoticz.Debug(indentStr + ">'" + x + "':'" + str(httpResp[x]) + "'")
            else:
                Domoticz.Debug(indentStr + ">'" + x + "':")
                DumpHTTPResponseToLog(httpResp[x], level+1)
    elif isinstance(httpResp, list):
        for x in httpResp:
            Domoticz.Debug(indentStr + "['" + x + "']")
    else:
        Domoticz.Debug(indentStr + ">'" + x + "':'" + str(httpResp[x]) + "'")
        
