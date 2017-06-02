# Pyrobus

[![Build Status](https://travis-ci.org/pollen/pyrobus.svg?branch=master)](https://travis-ci.org/pollen/pyrobus)

Pyrobus lets you easily connect, interact and program your [Robus](http://pollen-robotics.com) based robots.

The API was designed to be as simple as possible and let you focus on **bringing life to your ideas!**

<img src="http://pollen-robotics.com/assets/img/robus/code-example.gif" width=300px>

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

Pyrobus is a pure-python library and works with Python 2.7 or 3.4 and later.

## Quickstart

Pyrobus API was designed to be as simple as possible so you can directly focus on the application you want to make.

### Connecting

You can simply connect to your robot using one line.

#### On WiFi

```python
from robus import Robot

robot = Robot('my_robot_hostname.local')
```

#### On serial

```python
from robus import Robot

robot = Robot('my_serial_port')
```

#### Accessing values

Once connected the robot is automatically synced. You can access its plugged modules:

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

#### Linking sensor and effector in a loop

You can also transparently link sensors and effectors (even from different robots) together.

For instance:

```python
while True:
  if robot.dist_sensor.distance < 50:
    robot.led.color = (255, 0, 0)
  else:
    robot.led.color = (0, 0, 255)
```

### Robus gate API

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
      "value": [0, 255, 0]
    },
    "my_servo": {
      "position": 45
    }
  }
}
```

*Warning: you should not flood the robot with commands (pyrobus limits the push of commands to about 10Hz by default).*

## Metrics

The robus modules are automatically publishing usage information. This is  intended to help us better understand how people use our products and what we could improve. They published the names and types of the modules that are connected every minute.

The dedicated code is open-source and can be found [here](https://github.com/pollen/pyrobus/blob/master/robus/metrics.py).

## Contributing

Pyrobus was developped by the [Pollen Robotics](http://pollen-robotics.com/) team.

Pyrobus still needs lots of usage and testing to help it become more useful and reliable. If you are actively using Pyrobus, have suggestion or comments  please let us know!

Do not hesitate to share your experience with Pyrobus our meet other Robus users on our [forum](http://forum.pollen-robotics.com/)!

## License

Pyrobus is licensed under the [MIT license](./LICENSE).
