# Changelog

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
