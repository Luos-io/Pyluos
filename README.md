# Pyrobus

[![Build Status](https://travis-ci.org/pollen/pyrobus.svg?branch=master)](https://travis-ci.org/pollen/pyrobus)

Pyrobus lets you easily connect, interact and program your [Robus](http://pollen-robotics.com) based robots.

The API was designed to be as simple as possible and let you focus on **bringing life to your ideas!**

*You can find more information on Robus on http://pollen-robotics.com.*

## Install Pyrobus

#### From pypi (master branch):

```bash
pip install pyrobus
```

#### Or clone from git:
```
git clone http://github.com/pollen-robotics/pyrobus.git
```

#### Compatibility

Pyrobus is a pure-python library and works with Python >= 2.7 or 3.4 and later.

## Quickstart

Pyrobus API was designed to be as simple as possible so you can directly focus on the application you want to make.

### Connecting

Connecting to your robot is really easy. It actually takes only two lines of code.

#### On WiFi

```python
from pyrobus import Robot

robot = Robot('my_robot_hostname.local')
```

#### On serial

```python
from pyrobus import Robot

robot = Robot('my_serial_port')
```

*If you don't know how to find the name of the usb/wifi gate you are using, you can report to the section [Finding  a gate](#finding-a-gate).*

#### Accessing values

Once connected the robot is automatically synced at a high frequency. You can list the plugged modules via:

```python
print(robot.modules)

>>> [<Motor alias="motor_1" id=2 state=90>,
     <Motor alias="motor_2" id=3 state=90>,
     <Distance alias="distance_sensor_1" id=4 state=6>]
```

Or access the current value of a sensor directly:

```python
print(robot.distance_sensor_1.distance)

>>> 45
```

#### Sending commands

You can send command value to the effectors in a similar way.

```python
robot.motor_1.position = 45
robot.led.color = (0, 255, 0)
```

*The orders are in fact buffered and are actually sent a very short time after (few ms).*

#### Linking sensor and effector in a loop

You can also transparently link sensors and effectors (even from different robots) together.

For instance, the following code will change the color of the led to red when there is something near the distance sensor and change it to blue otherwise:

```python
while True:
  if robot.dist_sensor.distance < 50:
    robot.led.color = (255, 0, 0)
  else:
    robot.led.color = (0, 0, 255)
```

## Module available

### Button

Read:
* *state* (possible value 'ON' or 'OFF')

### Distance

Read:
* *distance* (value in mm)

### Dynamixel Motor

Read:
* *position* (in degrees)

Write:
* *target_position* (in degrees)
* *target_speed* (maximum reachable speed in degrees per second)
* *compliant* (True/False set the motor in compliant or stiff mode)
* *wheel* (True/False set the motor in wheel or joint mode)

### RGB Led

Write:
* *color* (R, G, B) channels. Each channel must be in [0, 255]

### Potentiometer

Read:
* *position* (in degrees)

### Relay

Method:
* *on()*
* *off()*

### Servo

Write:
* *target_position* (in degrees)

### Stepper

Read:
* *position* (in mm)

Write:
* *target_position* (in mm)
* *target_speed* (in mm/s)

Method:
* *home()*
* *stop()*

## Finding a gate

If you don't know the name of a gate, you can easily find it using the ```pyrobus-usb-gate``` and ```pyrobus-wifi-gate``` command line utilities.

There should be automatically installed when you install pyrobus. They should be available in your path. From the terminal, you can run:

```pyrobus-wifi-gate discover```

This will show the name of the wifi gate connected on the same WiFi. This uses the Zeroconf protocol.

*Make sure to use either the IP or the hostname.local for WiFi gates.*

Similarly, to find the name of the USB gate connected to your machine you can run:
```pyrobus-usb-gate discover```

You can then uses the found name to connect to it via pyrobus:

```python
from pyrobus import Robot
robot = Robot('/dev/cu.usbmodem2964691')
```

## Module Hotplug

At the moment, pyrobus does not support module hotplug. If you connect to a Robot and add a new module, they will not be automatically added to your Python object.

You will need to close it and re-create it.

```python
from pyrobus import Robot

robot = Robot('my_robot.local')

# Now physically hotplug a new modules

# The module will not show in:
print(robot.modules)

# First, closes the robot
robot.close()

# Re-creates it
robot = Robot('my_robot.local')

# Now the new module will show in:
print(robot.modules)
```

*This may be made automatic in future versions. Yet, this is unclear how to do that in a really seamless interaction.*

## Robus gate external API

If you want to connect your robot to other services, you can directly use its API. This JSON API is served either via the serial communication or via a websocket for the WiFi module.

The robot publish its state at a predefined frequency (currently about 40Hz). The state looks like:

```JSON
{
  "modules": [
    {
      "alias": "my_wifi_gate",
      "id": 1,
      "type": "gate"
    },
    {
      "alias": "my_button",
      "id": 2,
      "type": "button",
      "value": 1
    },
    {
      "alias": "my_left_arm",
      "id": 3,
      "type": "servo",
    }
  ]
}
```

You can also send commands using:

```JSON
{
  "modules": {
    "my_led": {
      "color": [0, 255, 0]
    },
    "my_servo": {
      "target_position": 45
    }
  }
}
```

You can find the list of all available registers in the [modules](#module-available) section.

*Warning: you should not flood the robot with commands as the gates are not protected against this at the moment. They will simply crash and reboot. Pyrobus for instance limits the push of commands to about the same frequency as it gets update from the robot (~10Hz).*

## Metrics

The robus modules are automatically publishing usage information. This is  intended to help us better understand how people use our products and what we could improve. They published the names and types of the modules that are connected every minute.

The dedicated code is open-source and can be found [here](https://github.com/pollen/pyrobus/blob/master/pyrobus/metrics.py).

## Contributing

Pyrobus was developed by the [Pollen Robotics](http://pollen-robotics.com/) team.

Pyrobus still needs lots of usage and testing to help it become more useful and reliable. If you are actively using Pyrobus, have suggestion or comments  please let us know!

Do not hesitate to share your experience with Pyrobus our meet other Robus users on our [forum](http://forum.pollen-robotics.com/)!

## License

Pyrobus is licensed under the [MIT license](./LICENSE).
