#!/usr/bin/env python3


import http.server
import shutil
import io

from player import Player, releasing


STATUS_PATH = '/status'
TOGGLE_PAUSE_PATH = '/togglepause'
INCREASE_VOLUME_PATH = '/increasevolume'
DECREASE_VOLUME_PATH = '/decreasevolume'

PLAY_PATH_PREFIX = '/play/'


with releasing(Player()) as player:
    class RequestHandler(http.server.SimpleHTTPRequestHandler):

        def do_GET(self) -> None:
            if self.path == STATUS_PATH:
                self.serve_status()
            else:
                super().do_GET()

        def do_POST(self) -> None:
            if self.path == PAUSE_PATH:
                player.pause()
            elif self.path == INCREASE_VOLUME_PATH:
                player.increase_volume()
            elif self.path == DECREASE_VOLUME_PATH:
                player.decrease_volume()
            elif self.path.startswith(PLAY_PATH_PREFIX):
                self.handle_play_request()
            else:
                super().do_POST()

        def handle_play_request(self) -> None:
            song = self.path[len(PLAY_PATH_PREFIX):]
            player.play(song)
            self.serve_status()

        def serve_status(self) -> None:
            status = str.encode(player.status_json())
            self.wfile.write(status)

    
    server_address = ('', 8000)
    server = http.server.HTTPServer(server_address, RequestHandler)
    server.serve_forever()

