
# Withings HealthMate

A Nodeserver to integrate the Withings lines of health monitors for use in
home automation.

### Requirements
* ISY994i Firmware 5.x
* Polyglot or Polisy
  * Requires Network Module or ISY Portal
* One or more Withings devices
* Healthmate Web access

### Installation
* Install from the Polyglot Nodeserver store

### Device Support
* Body Scales
  * Body
  * Smart Kid Scale
  * Smart Body Analyzer
  * Body+
  * Body Cardio
* Activity Trackers
  * Move
  * Steel
  * Activity Pop
  * Activity Go
  * Steel HR
  * Pulse HR
* Blood Pressure Monitor
* Sleep Sensor
  * Aura Sensor
  * Sleep Sensor/Monitor (New)

### Configuration
* Ensure you have your Withings credentials as they are needed to setup the 
Nodeserver authentication.
* Install the Nodeserver through the Polyglot store
* A Notice will appear with a link.  This notice will persist to allow you to add
additional users or accounts in the future.
* Click the link to go to the Withings authentication site.  Enter your credentials
and you will be redirected back to the Polyglot interface.
* Nodes for the discovered Withings devices will be created

### Usage
* Nodes status can be used as program triggers
* In/Out of bed notification is performed through a Polyglot callback.  The callback URL
was registered with Withings during the configuration.  In the event this stops for any reason 
you can Discover nodes again and this will re-create the subscription.