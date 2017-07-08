import time

from contextlib import closing

from zeroconf import ServiceBrowser, Zeroconf


class MyListener(object):
    wifi_gates = set()

    def remove_service(self, zeroconf, type, name):
        self.wifi_gates.remove(name)

    def add_service(self, zeroconf, type, name):
        self.wifi_gates.add(name)


def discover():
    with closing(Zeroconf()) as zeroconf:
        listener = MyListener()
        listener.wifi_gates.clear()

        browser = ServiceBrowser(zeroconf, "_jsongate._tcp.local.", listener)

        time.sleep(1.0)

        gates = [g.replace('._jsongate._tcp', '')[:-1]
                 for g in listener.wifi_gates]

        return {
            host.replace('.local', ''): (host, 9342)
            for host in gates
        }


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', choices=('discover', ))
    args = parser.parse_args()

    if args.cmd == 'discover':
        while True:
            print(discover())


if __name__ == '__main__':
    main()
