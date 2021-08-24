from .service import Service


class Pipe(Service):

    def __init__(self, id, alias, device):
        Service.__init__(self, 'Pipe', id, alias, device)
