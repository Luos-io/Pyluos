import os
import re

from jinja2 import Template

DEFAULT_TEMPLATE = os.path.join(os.path.dirname(__file__), 'extension.tpl.js')

supported_modules = [
    'button',
    'dynamixel',
    'l0_dc_motor',
    'l0_gpio',
    'l0_servo',
    'led',
    'potard',
]


def find_modules(state, type):
    return [
        str(m['alias'])
        for m in state['modules']
        if m['type'] == type
    ]


def find_xl320(state, dxl):
    dxl = next(filter(lambda mod: mod['alias'] == dxl, state['modules']))
    motors = [m for m in dxl if re.match(r'm[0-9]+', m)]
    return motors


def generate_extension(name,
                       robot,
                       host,
                       port,
                       template=DEFAULT_TEMPLATE):
    context = {}
    context = {
        'name': name,
        'host': host,
        'port': port,
    }
    context.update({
        type: find_modules(robot._state, type)
        for type in supported_modules
    })

    if context['dynamixel']:
        # TODO: This should be done for every dxl controller!
        context['xl_320'] = find_xl320(robot._state, context['dynamixel'][0])

    with open(template) as f:
        tpl = Template(f.read())
        ext = tpl.render(**context)
        return ext
