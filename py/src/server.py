#!/usr/bin/env python3


'''
Request formats
/play:title to play a song with a certain title.
/index to show the index interface.

Possible additions: /cache to browse cached music, /clear to remove something from cache.
'''


import http.server
import urllib
import shutil
import io

from jukebox import Jukebox


STATUS_PATH = '/status'


class HTTPHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self)

    def do_POST(self) -> None:
        def parse_song_title(path: str) -> str:
            return ''

        if self.path.startswith(PLAY_PATH_PREFIX):
            song_title = parse_song_title(self.path)
            play_song(song_title)

    def serve_data(self, data: bytes) -> None:
        pass


def play_song(song_title: str) -> None:
    pass


server_address = ('', 8000)
server = http.server.HTTPServer(server_address, HTTPHandler)
server.serve_forever()

