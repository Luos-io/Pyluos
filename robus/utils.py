import socket


def resolve_hostname(hostname, port):
    # We do our own mDNS resolution
    # to enforce we only search for IPV4 address
    # and avoid a 5s timeout in the websocket on the ESP
    # See https://github.com/esp8266/Arduino/issues/2110

    addrinfo = socket.getaddrinfo(hostname, port,
                                  socket.AF_INET, 0,
                                  socket.SOL_TCP)
    addr = addrinfo[0][4][0]
    return addr
