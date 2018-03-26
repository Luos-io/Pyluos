from subprocess import call
from tempfile import NamedTemporaryFile

from flask import Flask


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('host')
    args = parser.parse_args()

    with NamedTemporaryFile() as f:
        call(['python', 'generate-ext.py', args.host, '-o', f.name])
        extension_string = f.read()

    app = Flask(__name__)

    @app.route('/scratch-extension')
    def extension():
        return extension_string

    app.run()


if __name__ == '__main__':
    main()
