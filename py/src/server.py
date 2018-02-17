#!/usr/bin/env python3


import http
import http.server
import shutil
import urllib.parse
import io


from player import YoutubePlayer, releasing


STATUS_PATH = '/status'
TOGGLE_PAUSE_PATH = '/togglepause'
INCREASE_VOLUME_PATH = '/increasevolume'
DECREASE_VOLUME_PATH = '/decreasevolume'

PLAY_PATH_PREFIX = '/play/'


class InvalidRequest(BaseException):

    pass


with releasing(YoutubePlayer()) as player:
    class RequestHandler(http.server.SimpleHTTPRequestHandler):

        def do_GET(self) -> None:
            if self.path == STATUS_PATH:
                self.serve_status()
            else:
                super().do_GET()

        def do_POST(self) -> None:
            def interpret_request() -> None:
                if self.path == TOGGLE_PAUSE_PATH:
                    player.toggle_pause()
                elif self.path == INCREASE_VOLUME_PATH:
                    player.increase_volume()
                elif self.path == DECREASE_VOLUME_PATH:
                    player.decrease_volume()
                elif self.path.startswith(PLAY_PATH_PREFIX):
                    self.handle_play_request()
                else:
                    raise InvalidRequest 

            try:
                interpret_request()
                self.send_response(http.HTTPStatus.OK)
                self.end_headers()
            except InvalidRequest:
                self.send_error(http.HTTPStatus.BAD_REQUEST)

        def handle_play_request(self) -> None:
            def parse_song(path: str) -> str:
                quoted_song = self.path[len(PLAY_PATH_PREFIX):]
                return urllib.parse.unquote(quoted_song)

            song = self.path[len(PLAY_PATH_PREFIX):]
            player.play(song)
            self.serve_status()

        def serve_status(self) -> None:
            status = str.encode(player.status_json())
            self.wfile.write(status)

    
    server_address = ('', 8000)
    server = http.server.HTTPServer(server_address, RequestHandler)
    server.serve_forever()

