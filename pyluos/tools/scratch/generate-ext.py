import os
import re

from contextlib import closing
from jinja2 import Template
from pyluos import Robot

DEFAULT_TEMPLATE = os.path.join(os.getcwd(), 'extension.tpl.js')

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
        m['alias']
        for m in state['modules']
        if m['type'] == type
    ]


def find_xl320(state, dxl):
    dxl = next(filter(lambda mod: mod['alias'] == dxl, state['modules']))
    motors = [m for m in dxl if re.match(r'm[0-9]+', m)]
    return motors


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('host')
    parser.add_argument('--output-file', '-o')
    parser.add_argument('--template', '-t', default=DEFAULT_TEMPLATE)
    parser.add_argument('--name', '-n', default='luos')
    args = parser.parse_args()

    context = {
        'name': args.name,
        'host': args.host,
        'port': 9342,
    }
    with closing(Robot(args.host)) as r:
        context.update({
            type: find_modules(r._state, type)
            for type in supported_modules
        })

    if context['dynamixel']:
        # TODO: This should be done for every dxl controller!
        context['xl_320'] = find_xl320(r._state, context['dynamixel'][0])

    with open(args.template) as f:
        tpl = Template(f.read())
        ext = tpl.render(**context)

    if args.output_file:
        with open(args.output_file, 'w') as f:
            f.write(ext)
    else:
        print(ext)


if __name__ == '__main__':
    main()
