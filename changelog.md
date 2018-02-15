# Changelog

#### Version 0.9.5

Add another workaround for the send detection which seems to be sometimes unreceived on the gate side.

#### Version 0.9.4

Add a workaround to wait for the auto-baudrate to be ready.

#### Version 0.9.3

Fix https://github.com/pollen-robotics/robus-gate/pull/11

#### Version 0.9.2

Hotfix pinout for the L0-GPIO driver.

#### Version 0.9.1

Hotfix pinout for the L0-GPIO driver.

### Version 0.9

Add support for L0 GPIO module.

### Version 0.8

Rename for *pyluos*

### Version 0.7

Add support for stepper motors.
Improve USB gate discovery: now based on the manufacturer id.

#### Version 0.6.1

Add a convenience discovery method in the Serial.

### Version 0.6

Add the possibility to rename modules.

#### Version 0.5.1

Remove the smart sent of commands to circumvent reception issues within Robus.

### Version 0.5

Change the poll method for the serial port. It makes a huge impact on the CPU.

#### Version 0.4.1

Features:
* Install the discovery and scratch utilities as console scripts.

### Version 0.4

Features:
* Gates discovery
  * USB: using a white list
  * WiFi: using zeroconf
* USB gate redirection to Websocket
* Scratch broker

#### Version 0.3.1

Misc:
* Make zmq and ipywidgets optional dependencies to simplify installation.

### Version 0.3

Features:
* Start the detection at connection
* Add multiple registers support for dynamixel
* Properly close the robot/io

Bugfix:
* Improve communication robustness
* flush io after crashes

#### Version 0.2.1

Bugfix:
* Fix a speed/position conversion in the servo module on Python 2.7.

Misc:
* Improve unit tests coverage.

### Version 0.2

Features:
* Add speed control for servo
* Add zmq broker for visualisation

Bugfix:
* Prevent command spamming that could crashed the websocket connection

### Version 0.1

Features:
* Add modules: servo, led, potentiometer, distance, button
