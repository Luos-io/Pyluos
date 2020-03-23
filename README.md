# Pyluos

[![Build Status](https://travis-ci.org/pollen-robotics/pyluos.svg?branch=master)](https://travis-ci.org/pollen-robotics/pyluos)

Pyluos lets you easily connect, interact and program your [luos](https://www.luos.io) based devices.

The API was designed to be as simple as possible and let you focus on **bringing life to your ideas!**

*You can find more information on luos on https://www.luos.io.*

## Install Pyluos

#### From pypi (master branch):

```bash
pip install pyluos
```

#### Or clone from git:
```
git clone https://github.com/Luos-io/pyluos
```

#### Compatibility

Pyluos is a pure-python library and works with Python >= 2.7 or 3.4 and later.

## Quickstart

Pyluos API was designed to be as simple as possible so you can directly focus on the application you want to make!

### Connecting

Connecting to your device is really easy. It actually takes only two lines of code.

#### On WiFi

```python
from pyluos import Device

device = Device('my_robot_hostname.local')
```

#### On serial

```python
from pyluos import Device

device = Device('my_serial_port')
```

*If you don't know how to find the name of the usb/wifi gate you are using, you can report to the section [Finding  a gate](#finding-a-gate).*

#### Accessing values

Once connected the device is automatically synced at a high frequency. You can list the plugged modules via:

```python
print(device.modules)

>>> [<Motor alias="motor_1" id=2 state=90>,
     <Motor alias="motor_2" id=3 state=90>,
     <Distance alias="distance_sensor_1" id=4 state=6>]
```

Or access the current value of a sensor directly:

```python
print(device.distance_sensor_1.distance)

>>> 45
```

#### Sending commands

You can send command value to the effectors in a similar way.

```python
device.motor_1.position = 45
device.led.color = (0, 255, 0)
```

*The orders are in fact buffered and are actually sent a very short time after (few ms).*

#### Linking sensor and effector in a loop

You can also transparently link sensors and effectors (even from different devices) together.

For instance, the following code will change the color of the led to red when there is something near the distance sensor and change it to blue otherwise:

```python
while True:
  if device.dist_sensor.distance < 50:
    device.led.color = (255, 0, 0)
  else:
    device.led.color = (0, 0, 255)
```

## Available module

### L0 GPIO

Read - Input Pins:
* *p1* (analog input as u16)
* *p8* (digital input high/low)
* *p9* (digital input high/low)
* *p10* (digital input high/low)
* *p11* (digital input high/low)
* *p12* (analog input as u16)

Write - Output Pins:
* *p2* (digital output high/low)
* *p3* (digital output high/low)
* *p4* (digital output high/low)

### Button

Read:
* *state* (possible value 'ON' or 'OFF')

### Potentiometer

Read:
* *position* (in degrees)

## Coming soon

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

If you don't know the name of a gate, you can easily find it using the ```pyluos-usb-gate``` and ```pyluos-wifi-gate``` command line utilities.

There should be automatically installed when you install Pyluos. They should be available in your path. From the terminal, you can run:

```pyluos-wifi-gate discover```

This will show the name of the wifi gate connected on the same WiFi. This uses the Zeroconf protocol.

*Make sure to use either the IP or the hostname.local for WiFi gates.*

Similarly, to find the name of the USB gate connected to your machine you can run:
```pyluos-usb-gate discover```

You can then uses the found name to connect to it via Pyluos:

```python
from pyluos import Device
device = Device('/dev/cu.usbmodem2964691')
```

## Module Hotplug

At the moment, Pyluos does not support module hotplug. If you connect to a Robot and add a new module, they will not be automatically added to your Python object.

You will need to unplug the whole bus and re-power it.

*This may be made automatic in future versions.*

## Luos gate external API

If you want to connect your device to other services, you can directly use its API. This JSON API is served either via the serial communication or via a websocket for the WiFi module.

The device publish its state at a predefined frequency (currently about 25Hz). The state looks like:

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

*Warning: you should not flood the robot with commands as the gates are not protected against this at the moment. They will simply crash and reboot. Pyluos for instance limits the push of commands to about the same frequency as it gets update from the robot (~25Hz).*

## Contributing

Pyluos was developed by the [Pollen Robotics](http://pollen-robotics.com/) team as part of [Luos](https://www.luos.io).

Pyluos still needs lots of usage and testing to help it become more useful and reliable. If you are actively using Pyluos, have suggestion or comments  please let us know!

Do not hesitate to share your experience with Pyluos our meet other luos users on our [forum](https://community.luos.io)!

## License

Pyluos is licensed under the [MIT license](./LICENSE).
