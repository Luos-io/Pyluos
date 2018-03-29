const ArgumentType = Scratch.ArgumentType;
const BlockType = Scratch.BlockType;

const blockIconURI = 'data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiA/PjwhRE9DVFlQRSBzdmcgIFBVQkxJQyAnLS8vVzNDLy9EVEQgU1ZHIDEuMS8vRU4nICAnaHR0cDovL3d3dy53My5vcmcvR3JhcGhpY3MvU1ZHLzEuMS9EVEQvc3ZnMTEuZHRkJz48c3ZnIGVuYWJsZS1iYWNrZ3JvdW5kPSJuZXcgMCAwIDI0IDI0IiBoZWlnaHQ9IjI0cHgiIGlkPSJMYXllcl8xIiB2ZXJzaW9uPSIxLjEiIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjI0cHgiIHhtbDpzcGFjZT0icHJlc2VydmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiPjxnPjxwYXRoIGQ9Ik0yMywxMWgtMVY0LjZDMjIsNC4xLDIxLjYsNCwyMSw0aC03LjZsMi45LTMuMWMwLjItMC4yLDAuMy0wLjQtMC4xLTAuN2MtMC4zLTAuMy0wLjYsMC0wLjgsMC4yTDEyLDRoMEw4LjUsMC4zICAgQzguMywwLjEsNy45LTAuMiw3LjYsMC4xcy0wLjIsMC42LDAsMC44bDMsMy4xSDNDMi40LDQsMiw0LjEsMiw0LjZWMTFIMWMtMC42LDAtMSwwLjEtMSwwLjZ2NEMwLDE2LjIsMC40LDE3LDEsMTdoMXY1LjYgICBDMiwyMy4yLDIuNCwyNCwzLDI0aDE4YzAuNiwwLDEtMC44LDEtMS40VjE3aDFjMC42LDAsMS0wLjgsMS0xLjR2LTRDMjQsMTEuMSwyMy42LDExLDIzLDExeiBNMSwxNnYtNGgydjRIMXogTTIwLDIySDRWNmgxNlYyMnogICAgTTIzLDE2aC0ydi00aDJWMTZ6Ii8+PHBhdGggZD0iTTE2LDguNmMtMS4xLDAtMiwwLjktMiwyczAuOSwyLDIsMnMyLTAuOSwyLTJTMTcuMSw4LjYsMTYsOC42eiBNMTYsMTEuNmMtMC42LDAtMS0wLjQtMS0xczAuNC0xLDEtMXMxLDAuNCwxLDEgICBTMTYuNiwxMS42LDE2LDExLjZ6Ii8+PHBhdGggZD0iTTgsMTIuNmMxLjEsMCwyLTAuOSwyLTJzLTAuOS0yLTItMnMtMiwwLjktMiwyUzYuOSwxMi42LDgsMTIuNnogTTgsOS42YzAuNiwwLDEsMC40LDEsMXMtMC40LDEtMSwxcy0xLTAuNC0xLTEgICBTNy40LDkuNiw4LDkuNnoiLz48cGF0aCBkPSJNMTcsMTdjMC0wLjYtMC40LTEtMS0xSDhjLTAuNiwwLTEsMC40LTEsMXYyYzAsMC42LDAuNCwxLDEsMWg4YzAuNiwwLDEtMC40LDEtMVYxN3ogTTgsMTguNnYtMmgydjJIOHogTTExLDE4LjZ2LTJoMnYySDExICAgeiBNMTYsMTguNmgtMnYtMmgyVjE4LjZ6Ii8+PC9nPjwvc3ZnPg==';


class LuosClient {
    constructor (host, port) {
        this.cmd = {};
        this.state = {};

        this.ws = new WebSocket(`ws://${host}:${port}`);
        this.ws.onopen = this.startDetection.bind(this);
        this.ws.onmessage = this.onstate.bind(this);
    }
    onstate (msg) {
        const data = JSON.parse(msg.data);

        const state = {};
        data.modules.forEach(mod => {
            state[mod.alias] = mod;
        });
        this.state = state;

        if (Object.keys(this.cmd).length !== 0) {
            this.send({modules: this.cmd});
            this.cmd = {};
        }
    }
    get (alias, reg) {
        if (alias in this.state && reg in this.state[alias]) {
            return this.state[alias][reg];
        }
    }
    set (alias, reg, value) {
        if (!alias) {
            return;
        }
        if (!(alias in this.cmd)) {
            this.cmd[alias] = {};
        }
        this.cmd[alias][reg] = value;
    }
    startDetection () {
        this.send({detection: {}});
    }
    send (msg) {
        this.ws.send(JSON.stringify(msg));
    }
}

class Scratch3LuosBlocks {
    constructor (runtime) {
        this.runtime = runtime;
        this.robot = new LuosClient('{{ host }}', {{ port }});
    }
    getInfo () {
        return {
            id: '{{ name }}',
            name: '{{ name|capitalize }}',
            blockIconURI: blockIconURI,
            blocks: [
                {% if button %}
                {
                    opcode: 'buttonPressed',
                    blockType: BlockType.BOOLEAN,
                    text: '[BUTTON] pressed',
                    arguments: {
                        BUTTON: {
                            type: ArgumentType.STRING,
                            menu: 'foundButtons'
                        }
                    }
                },
                {
                    opcode: 'whenButtonPressed',
                    blockType: BlockType.HAT,
                    text: 'when [BUTTON] is pressed',
                    arguments: {
                        BUTTON: {
                            type: ArgumentType.STRING,
                            menu: 'foundButtons'
                        }
                    },
                    func: 'buttonPressed'
                },
                {% endif %}
                {% if potard %}
                {
                    opcode: 'potentiometerPosition',
                    blockType: BlockType.REPORTER,
                    text: '[POTENTIOMETER] position',
                    arguments: {
                        POTENTIOMETER: {
                            type: ArgumentType.STRING,
                            menu: 'foundPotentiometers'
                        }
                    }
                },
                {% endif %}
                {% if led %}
                {
                    opcode: 'setLedColor',
                    blockType: BlockType.COMMAND,
                    text: 'set [LED] color to [COLOR]',
                    arguments: {
                        LED: {
                            type: ArgumentType.STRING,
                            menu: 'foundLeds'
                        },
                        COLOR: {
                            type: ArgumentType.COLOR
                        }
                    }
                },
                {% endif %}
                {% if l0_servo %}
                {
                    opcode: 'setServoPosition',
                    blockType: BlockType.COMMAND,
                    text: 'set [SERVO] [S] position to [POS]',
                    arguments: {
                        SERVO: {
                            type: ArgumentType.STRING,
                            menu: 'foundServos'
                        },
                        S: {
                            type: ArgumentType.STRING,
                            menu: 'servo'
                        },
                        POS: {
                            type: ArgumentType.NUMBER
                        }
                    }
                },
                {% endif %}
                {% if l0_dc_motor %}
                {
                    opcode: 'setDCSpeed',
                    blockType: BlockType.COMMAND,
                    text: 'set [DC] [M] speed to [SPEED]',
                    arguments: {
                        DC: {
                            type: ArgumentType.STRING,
                            menu: 'foundDCs'
                        },
                        M: {
                            type: ArgumentType.STRING,
                            menu: 'DCMotor'
                        },
                        SPEED: {
                            type: ArgumentType.NUMBER
                        }
                    }
                },
                {% endif %}
                {% if l0_gpio %}
                {
                    opcode: 'gpioDigitalInput',
                    blockType: BlockType.BOOLEAN,
                    text: 'Is [GPIO] pin [DIGITAL_IN] high?',
                    arguments: {
                        GPIO: {
                            type: ArgumentType.STRING,
                            menu: 'foundGPIOs'
                        },
                        DIGITAL_IN: {
                            type: ArgumentType.STRING,
                            menu: 'digitalIn'
                        }
                    }
                },
                {
                    opcode: 'gpioDigitalOutput',
                    blockType: BlockType.COMMAND,
                    text: 'set [GPIO] pin [DIGITAL_OUT] to [LEVEL]',
                    arguments: {
                        GPIO: {
                            type: ArgumentType.STRING,
                            menu: 'foundGPIOs'
                        },
                        DIGITAL_OUT: {
                            type: ArgumentType.STRING,
                            menu: 'digitalOut'
                        },
                        LEVEL: {
                            type: ArgumentType.STRING,
                            menu: 'digitalLevel'
                        }
                    }
                },
                {
                    opcode: 'gpioAnalogInput',
                    blockType: BlockType.REPORTER,
                    text: '[GPIO] read pin [ANALOG_PIN] value',
                    arguments: {
                        GPIO: {
                            type: ArgumentType.STRING,
                            menu: 'foundGPIOs'
                        },
                        ANALOG_PIN: {
                            type: ArgumentType.STRING,
                            menu: 'analogPin'
                        }
                    }
                },
                {
                    opcode: 'gpioPwmDutyCycle',
                    blockType: BlockType.COMMAND,
                    text: 'set [GPIO] pwm [PWM_PIN] duty cycle to [DUTY] %',
                    arguments: {
                        GPIO: {
                            type: ArgumentType.STRING,
                            menu: 'foundGPIOs'
                        },
                        PWM_PIN: {
                            type: ArgumentType.STRING,
                            menu: 'pwmPin'
                        },
                        DUTY: {
                            type: ArgumentType.NUMBER
                        }
                    }
                },
                {% endif %}
                {% if dynamixel %}
                {
                    opcode: 'dxlPresentPosition',
                    blockType: BlockType.REPORTER,
                    text: '[DXL] [MOTOR] position',
                    arguments: {
                        DXL: {
                            type: ArgumentType.STRING,
                            menu: 'foundDxls'
                        },
                        MOTOR: {
                            type: ArgumentType.STRING,
                            menu: 'foundXL320s'
                        }
                    }
                },
                {
                    opcode: 'dxlTargetPosition',
                    blockType: BlockType.COMMAND,
                    text: 'set [DXL] [MOTOR] target position to [POS]',
                    arguments: {
                        DXL: {
                            type: ArgumentType.STRING,
                            menu: 'foundDxls'
                        },
                        MOTOR: {
                            type: ArgumentType.STRING,
                            menu: 'foundXL320s'
                        },
                        POS: {
                            type: ArgumentType.NUMBER
                        }
                    }
                },
                {
                    opcode: 'dxlMovingSpeed',
                    blockType: BlockType.COMMAND,
                    text: 'set [DXL] [MOTOR] maximum speed to [SPEED]',
                    arguments: {
                        DXL: {
                            type: ArgumentType.STRING,
                            menu: 'foundDxls'
                        },
                        MOTOR: {
                            type: ArgumentType.STRING,
                            menu: 'foundXL320s'
                        },
                        SPEED: {
                            type: ArgumentType.NUMBER
                        }
                    }
                },
                {
                    opcode: 'dxlCompliant',
                    blockType: BlockType.COMMAND,
                    text: 'set [DXL] [MOTOR] [COMPLIANT]',
                    arguments: {
                        DXL: {
                            type: ArgumentType.STRING,
                            menu: 'foundDxls'
                        },
                        MOTOR: {
                            type: ArgumentType.STRING,
                            menu: 'foundXL320s'
                        },
                        COMPLIANT: {
                            type: ArgumentType.STRING,
                            menu: 'compliancy'
                        }
                    }
                },
                {% endif %}
            ],
            menus: {
                {% if button %}
                  foundButtons: {{ button }},
                {% endif %}
                {% if l0_dc_motor %}
                  foundDCs: {{ l0_dc_motor }},
                  DCMotor: ['m1', 'm2'],
                {% endif %}
                {% if dynamixel %}
                  foundDxls: {{ dynamixel }},
                  // TODO: this should be made for each dxl controller
                  // Something like
                  // {% for c in dxl %}
                  // foundXL320_{{ c }}: {{ xl_320[c] }}
                  // {% endfor %}
                  foundXL320s: {{ xl_320 }},
                  compliancy: ['compliant', 'stiff'],
                {% endif %}
                {% if l0_gpio %}
                  foundGPIOs: {{ l0_gpio }},
                  digitalIn: ['p5', 'p6'],
                  digitalOut: ['p3', 'p4'],
                  analogPin: ['p7', 'p8', 'p9'],
                  pwmPin: ['p1', 'p2'],
                  digitalLevel: ['low', 'high'],
                {% endif %}
                {% if led %}
                  foundLeds: {{ led }},
                {% endif %}
                {% if potard %}
                  foundPotentiometers: {{ potard }},
                {% endif %}
                {% if l0_servo %}
                  foundServos: {{ l0_servo }},
                  servo: ['s1', 's2', 's3', 's4'],
                {% endif %}
            }
        };
    }
    {% if button %}
    buttonPressed (args) {
        const val = this.robot.get(args.BUTTON, 'state');
        if (typeof val !== 'undefined') {
            return val === 1;
        }
    }
    {% endif %}
    {% if potard %}
    potentiometerPosition (args) {
        const pos = this.robot.get(args.POTENTIOMETER, 'position');
        return 300 * pos / 4096;
    }
    {% endif %}
    {% if led %}
    setLedColor (args) {
        const hexToRgb = hex => {
            const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
            return result ? [
                parseInt(result[1], 16),
                parseInt(result[2], 16),
                parseInt(result[3], 16)
            ] : null;
        };

        this.robot.set(args.LED, 'rgb', hexToRgb(args.COLOR));
    }
    {% endif %}
    {% if l0_servo %}
    setServoPosition (args) {
        let pos = parseFloat(args.POS);
        pos = Math.min(Math.max(pos, 0.0), 180.0);
        this.robot.set(args.SERVO, args.S.replace('s', 'p'), pos);
    }
    {% endif %}
    {% if l0_dc_motor %}
    setDCSpeed (args) {
        let speed = parseFloat(args.SPEED);
        speed = Math.min(Math.max(speed, -1.0), 1.0);
        this.robot.set(args.DC, args.M.replace('m', 's'), speed);
    }
    {% endif %}
    {% if l0_gpio %}
    gpioDigitalInput (args) {
        const val = this.robot.get(args.GPIO, args.DIGITAL_IN);
        if (typeof val !== 'undefined') {
            return val === 1;
        }
    }
    gpioDigitalOutput (args) {
        const val = args.LEVEL === 'high' ? 1 : 0;
        this.robot.set(args.GPIO, args.DIGITAL_OUT, val);
    }
    gpioAnalogInput (args) {
        return this.robot.get(args.GPIO, args.ANALOG_PIN);
    }
    gpioPwmDutyCycle (args) {
        let duty = parseFloat(args.DUTY);
        duty = Math.min(Math.max(duty, 0.0), 100.0);
        this.robot.set(args.GPIO, args.PWM_PIN, duty);
    }
    {% endif %}
    {% if dynamixel %}
    dxlPresentPosition (args) {
        const pos = this.robot.get(args.DXL, args.MOTOR);
        return 300 * (pos / 1024) - 150;
    }
    dxlTargetPosition (args) {
        let pos = parseFloat(args.POS);
        pos = Math.min(Math.max(-150.0, pos), 150.0);
        pos = (150 + pos) / 300 * 1024;
        pos = Math.min(Math.max(0, pos), 1023);
        pos = Math.floor(pos);
        this.robot.set(args.DXL, args.MOTOR, pos);
    }
    dxlMovingSpeed (args) {
        let speed = parseFloat(args.SPEED);

        if speed < 0 {
            let direction = 1024;
        } else {
            let direction = 0;
        }
        const speed_factor = 0.111;
        const max_value = 1023 * speed_factor * 6;
        speed = Math.min(Math.max(speed, -max_value), max_value);
        speed = parseInt(Math.round(direction + Math.abs(speed) / (6 * speed_factor), 0));

        this.robot.set(args.DXL, args.MOTOR.replace('m', 's'), );
    }
    dxlCompliant (args) {
        let compliant = args.COMPLIANT === 'compliant' ? true : false;
        this.robot.set(args.DXL, args.MOTOR.replace('m', 'c'), compliant);
    }
    {% endif %}
}

Scratch.extensions.register(new Scratch3LuosBlocks());
