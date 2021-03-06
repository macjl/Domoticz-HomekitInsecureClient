# Domoticz-HomekitInsecureClient

Domoticz plugin to connect to an Homkit device or bridge in Insecure Mode (Homebridge, Homekit Accessory Architect, etc...)

## Supported devices :
  - Switch Devices
  - Smart Plugs
  - Sprinkler, valves

## Installation
- Go to your plugins folder in domoticz
- Clone the repository : `git clone https://github.com/macjl/Domoticz-HomekitInsecureClient.git HomekitInsecureClient`
- Restart Domoticz

## Configuration
- Make sure the Homekit device you want to control allow 'Insecure' connections ([Homebridge](https://github.com/oznu/homebridge-config-ui-x/wiki/Enabling-Accessory-Control), [HAA](https://github.com/RavenSystem/esp-homekit-devices/wiki/General-Configuration#Enable-HomeKit-rest-API))
- Go to Hardware Configuration in Domoticz
- Add an Hardware with type "Homekit Insecure Client"
- Configure the plugin with the IP Address of the bridge, Port, and Authorization key (format : *xxx-xx-xxx*)
  > **_Note for homebridge users : you have to use the Homekit port you will find in config.json, not the port of the interface (homebridge-ui)_**
- The devices should appear in Unused Devices after 1 minute

## Is my device supported?
- You can show more informations by enabling "Plugin Debug" in Debug menu. It will show discoverd devices that are not supported yet. You can open an issue in Github with this logs, and I'll see if I can support it.
