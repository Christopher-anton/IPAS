import socket
import json

from pymemcache.client.base import Client


class Localization:
    def on_get(self, req, resp):
        """Return current location to client."""
        memcached_client = Client(('localhost', 11211))
        state = memcached_client.get('state')
        pos = {
            'x': 0,
            'y': 0,
            'z': 0,
        }
        if state:
            state = json.loads(state)
            pos['x'] = state['x']
            pos['y'] = state['y']
            pos['z'] = state['z']
        resp.body = json.dumps(pos)
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        """Move to specified location."""
        def get_coord(req, coord):
            try:
                c = int(req.get_param(coord))
            except ValueError, falcon.HttpInvalidHeader:
                return
            else:
                return c
        x = get_coord(req, 'x')
        y = get_coord(req, 'y')
        z = get_coord(req, 'z')
        if socket.gethostname().lower() in ('cera', 'littlefoot'):
            # Ground vechicle, call on the RobotControl Server to move
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server = ('localhost', 6579)
            client.bind((server[0], server[1]+1))
            client.settimeout(None)
            client.connect(server)
            client.sendall(f'goto:({x},{y})\n')
            data = client.recv(1)
            try:
                data = self.conn.recv(1)
                while data and data[-1] != ord('\n'):
                    data += self.conn.recv(1)
                if not data:
                    break
            except socket.error:
                break

            try:
                text = data.decode().strip()
            except UnicodeDecodeError:
                break

            if text.lower() == 'done':
                resp.status = falcon.HTTP_200
            else:
                resp.status = falcon.HTTP_500
        else:
            # UAV
            pass
