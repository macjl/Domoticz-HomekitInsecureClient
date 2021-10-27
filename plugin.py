# Connect to Homekit Device in Insecure mode
#
# Author: MacJL
#
"""
<plugin key="HomekitInsecureClient" name="Homekit Insecure Client" author="MacJL" version="2.1" wikilink="http://www.domoticz.com/wiki/plugins" externallink="https://github.com/macjl/Domoticz-HomekitInsecureClient">
    <description>
        Control Homekit Devices which are set in insecure mode (eg : Homebridge, HAA, etc...)
    </description>
    <params>
        <param field="Address" label="IP Address of homekit device or bridge" width="200px" required="true" default="127.0.0.1"/>
        <param field="Port" label="PORT of homekit device or bridge" width="50px" required="true" default="54821"/>
        <param field="Password" label="Authorization key" width="80px" required="true" default="031-45-154" password="true"/>
        <param field="Mode6" label="Debug" width="150px">
            <options>
                <option label="None" value="0"  default="true" />
                <option label="Plugin Debug" value="2"/>
                <option label="All" value="-1"/>      
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import json

class BasePlugin:
    enabled = False
    httpConnGet = None
    Timeout = 60000
    GetSent = 0
    headers = { 'Content-Type': 'Application/json'}

    def __init__(self):
        return

    def onStart(self):
        Domoticz.Debugging(int(Parameters["Mode6"]))
        Domoticz.Debug("Plugin set in Debug Mode")
        DumpConfigToLog()

        Domoticz.Log("Initializing Homekit Insecure Client Plugin")

        Domoticz.Debug("Creating Connection object")
        self.headers = { 'Content-Type': 'Application/json', 'Authorization': Parameters["Password"] }
        self.httpConnGet = Domoticz.Connection(Name="httpGET", Transport="TCP/IP", Protocol="HTTP", Address=Parameters["Address"], Port=Parameters["Port"])

        Domoticz.Log("Connecting to Homekit Device at address http://" + Parameters["Address"] + ":" + Parameters["Port"] )
        self.httpConnGet.Connect(Timeout=self.Timeout)

    def onStop(self):
        self.httpConnGet.Disconnect()
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        if (Status == 0):
            Domoticz.Debug("Connection successfull")
        else:
            Domoticz.Error("Failed to connect ("+str(Status)+") to: "+Parameters["Address"]+":"+Parameters["Port"]+" with error: "+Description)

    def onTimeout(self, Connection):
        Domoticz.Log("Timeout on Connection")
        Connection.Disconnect()

    def onMessage(self, Connection, Data):
        Domoticz.Debug("Data received")
        
        try:
            Status = int(Data["Status"])
        except:
            Domoticz.Error("Invalid Data : No status")
            Connection.Disconnect()
            return

        if (Status == 204):
            Domoticz.Debug( "Command sent")
            return
        elif (Status != 200):
            Domoticz.Error("Invalid Data received. Status=" + str( Status) )
            Connection.Disconnect()
            return

        # Get Accessories as a dict variable
        self.GetSent=0
        Domoticz.Debug( Data["Data"].decode("utf-8", "ignore") )
        accessories = json.loads( Data["Data"].decode("utf-8", "ignore") )["accessories"]
        for accessory in accessories:
            hkaid = accessory["aid"]
            supported = 0
            hkName="No Name"
            # Find if accessory is provided by eDomoticz and global name
            for service in accessory["services"]:
                if( service["type"] == "3E" ):
                    #Domoticz.Debug(str( service["characteristics"] ) )
                    for characteristic in service["characteristics"]:
                        if ( characteristic["type"] == "20" ):
                            hkManufacturer = characteristic["value"]
                        if ( characteristic["type"] == "23" ):
                            hkName = characteristic["value"]
            # If accessory is not provided by eDomoticz
            if ( hkManufacturer != "eDomoticz" ):
                for service in accessory["services"]:
                    # Service of type Smart Plug
                    if( service["type"] == "47" or service["type"] == "49" or service["type"] == "D0" ):
                        Domoticz.Debug(str( service["characteristics"] ) )
                        hkName="NoName"
                        for characteristic in service["characteristics"]:
                            if ( characteristic["type"] == "23" ):
                                hkName = characteristic["value"]
                            if ( characteristic["type"] == "25" or characteristic["type"] == "B0" ):
                                hkiid = characteristic["iid"]
                                hkValue = characteristic["value"]
                                if ( hkValue == True ): hkValue = 1
                                if ( hkValue == False ): hkValue = 0
                        deviceID = service["type"] + "-" + str( hkaid ) + "-" + str( hkiid )
                        domoticzID = GetIDFromDevID( deviceID )
                        Domoticz.Debug( hkManufacturer + " : " + hkName + " - DeviceID=" + deviceID + " - DomoticzID=" + str( domoticzID ) + " - Current Value=" + str (hkValue) )

                        if ( domoticzID == -1 ):
                            Domoticz.Debug("Create domoticz device :\"" + hkName + "\" with ID=" + str( len(Devices) + 1 ) + " and DeviceID=" + deviceID + " of type Switch")
                            Domoticz.Device(Name=hkName, Unit=len(Devices) + 1, TypeName="Switch", DeviceID=deviceID ).Create()
                            domoticzID = GetIDFromDevID( deviceID )
                            Domoticz.Log("Device created: " + hkName + " - DeviceID=" + deviceID )
                        IDX = Devices[domoticzID].ID
                        if ( hkValue != Devices[domoticzID].nValue ):
                            if ( hkValue == 1 ):
                                Domoticz.Log("Set ON  to Device " + hkName + " - IDX=" + str( IDX ) + " - DeviceID=" + deviceID + " - DomoticzID=" + str( domoticzID ) )
                                Devices[domoticzID].Update(nValue=1,sValue="On")
                            elif ( hkValue == 0 ):
                                Domoticz.Log("Set OFF to Device " + hkName + " - IDX=" + str( IDX ) + " - DeviceID=" + deviceID + " - DomoticzID=" + str( domoticzID ) )
                                Devices[domoticzID].Update(nValue=0,sValue="Off")
                            else:
                                Domoticz.Error("Invalid Homekit Data")
                    elif( service["type"] == "3E"):
                        pass
                    else:
                        Domoticz.Debug("Device " + hkManufacturer + " - AID=" + str( hkaid ) + " - Type of Service=" + service["type"] + " - Not supported yet")

    def onCommand(self, Unit, Command, Level, Hue):
        if ( Devices[Unit].sValue != Command ):
            if str(Command) == "On":
                Devices[Unit].Update(nValue=1,sValue="On")
                nValue = "1"
            if str(Command) == "Off":
                Devices[Unit].Update(nValue=0,sValue="Off")
                nValue = "0"

            deviceIDsplitted = Devices[Unit].DeviceID.split("-")
            aid = deviceIDsplitted[1]
            iid = deviceIDsplitted[2]

            Domoticz.Log("Command called for Unit=" + str(Unit) + " and DeviceID=" + Devices[Unit].DeviceID + ": Parameter '" + str(Command) + "'")
            data = "{\"characteristics\":[{\"aid\":" + aid + ",\"iid\":" + iid + ",\"value\":" + nValue + "}]}"
            Domoticz.Debug(data)

            try:
                self.httpConnGet.Send({'Verb':'PUT', 'URL':'/characteristics', 'Headers': self.headers, 'Data': data})
            except:
                Domoticz.Error("Problem sending command to accessory : " + data)

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("Connection " + Connection.Name + " disconnected")
        self.GetSent=0

    def onHeartbeat(self):
        Domoticz.Debug("Refreshing Accessories Status")
        if ( self.GetSent == 1 ):
            Domoticz.Debug("No Data received since last heartbeat. Disconnecting")
            self.httpConnGet.Disconnect()
            self.GetSent=0
        elif (self.httpConnGet != None and ( self.httpConnGet.Connected() )):
            Domoticz.Debug("Connection is alive. Sending /accessories command")
            self.httpConnGet.Send({'Verb':'GET', 'URL':'/accessories', 'Headers': self.headers})
            self.GetSent=1
        else:
            Domoticz.Log("Connection Lost. Reconnecting.")
            self.httpConnGet.Connect(Timeout=self.Timeout)

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

def onTimeout(Connection):
    global _plugin
    _plugin.onTimeout(Connection)

def onMessage(Connection, Data):
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

def GetIDFromDevID(devid):
    for Device in Devices:
        if ( devid == Devices[Device].DeviceID ):
            return Device
    return -1

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
        Domoticz.Debug("Device DeviceID : " + str(Devices[x].DeviceID))
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
        
