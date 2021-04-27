# Domoticz-HomekitInsecureClient

Domoticz plugin to connect to an Homkit device or bridge in Insecure Mode (Homebridge, Homekit Accessory Architect, etc...)

## Supported devices :
  - Switch Devices
  - Smart Plugs

## Installation
- Go to your plugins folder in domoticz
- Clone the repository : `git clone https://github.com/macjl/Domoticz-HomekitInsecureClient.git HomekitInsecureClient`
- Restart Domoticz

## Configuration
- Make sure the Homekit device you want to control allow 'Insecure' connections ([Homebridge](https://github.com/oznu/homebridge-config-ui-x/wiki/Enabling-Accessory-Control), [HAA](https://github.com/RavenSystem/esp-homekit-devices/wiki/General-Configuration#Enable-HomeKit-rest-API))
- Go to Hardware Configuration in Domoticz
- Add an Hardware with type "Homekit Insecure Client"
- Configure the plugin with the IP Address of the bridge, Port, and Authorization key (format : xxx-xx-xxx)
- The devices should appear in Unused Devices after 1 minute
