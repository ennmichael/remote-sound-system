#!/usr/bin/env python3


import http
import http.server
import shutil
import urllib.parse
import io
import contextlib
import json

import music


SONG_DATABASE_PATH = './db'
STATUS_PATH = '/status'
TOGGLE_PAUSE_PATH = '/togglepause'
INCREASE_VOLUME_PATH = '/increasevolume'
DECREASE_VOLUME_PATH = '/decreasevolume'
PLAY_PATH_PREFIX = '/play/'


class InvalidRequest(BaseException):

    pass


if __name__ == '__main__':
    def youtube_player() -> music.YoutubePlayer:
        return music.YoutubePlayer(SONG_DATABASE_PATH)

    with contextlib.closing(youtube_player()) as player:
        song_loop = music.SongLoop(player)

        class RequestHandler(http.server.SimpleHTTPRequestHandler):

            def do_GET(self) -> None:
                if self.path == STATUS_PATH:
                    self.end_response_ok()
                    self.serve_status()
                else:
                    super().do_GET()

            def do_POST(self) -> None:
                self.end_response_ok()

                def interpret_request() -> None:
                    if self.path == TOGGLE_PAUSE_PATH:
                        player.toggle_pause()
                        self.serve_status()
                    elif self.path == INCREASE_VOLUME_PATH:
                        player.increase_volume()
                        self.serve_status()
                    elif self.path == DECREASE_VOLUME_PATH:
                        player.decrease_volume()
                        self.serve_status()
                    elif self.path.startswith(PLAY_PATH_PREFIX):
                        self.serve_status()
                        self.handle_play_request()

                interpret_request()

            def end_response(self, status: http.HTTPStatus) -> None:
                self.send_response(status)
                self.end_headers()

            def end_response_ok(self) -> None:
                self.end_response(http.HTTPStatus.OK)

            def handle_play_request(self) -> None:
                def parse_song(path: str) -> str:
                    quoted_song = path[len(PLAY_PATH_PREFIX):]
                    return urllib.parse.unquote(quoted_song)

                song = parse_song(self.path)
                song_loop.add_song(song)

            def serve_status(self) -> None:
                status = player.status()
                status['songQueue'] = song_loop.song_queue
                status_json = json.dumps(status)
                self.wfile.write(str.encode(status_json))

        
        server_address = ('', 8000)
        server = http.server.HTTPServer(server_address, RequestHandler) 

        while True:
            song_loop.update()
            server.handle_request()

