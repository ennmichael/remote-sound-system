#!/usr/bin/env python3


from typing import Iterator, NamedTuple, TypeVar, Generic, Dict
import contextlib
import collections
import pathlib
import json

import vlc
import pafy
import requests
from pyquery import PyQuery


class SongNotCached(BaseException):

    pass


def song_media(song: str) -> vlc.Media:
    search_hit = find_on_youtube(song)

    try:
        return cached_song_media(search_hit.title)
    except SongNotCached:
        return online_song_media(search_hit.url)


def cached_song_media(title: str) -> vlc.Media:
    path = f'db/{title}'

    if not file_exists(path):
        raise SongNotCached
    
    return vlc.Media(f'db/{title}')


def file_exists(path: str) -> bool:
    return pathlib.Path(path).is_file()


def online_song_media(url: str) -> vlc.Media:
    return vlc.Media(url)


class YoutubeSearchHit(NamedTuple):

    title: str
    url: str


def find_on_youtube(search_query: str) -> YoutubeSearchHit:
    def get_html(search_query: str) -> str:
        spoofed_headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'
        }

        payload = {
            'search_query': search_query
        }
        
        response = requests.get(
            'https://www.youtube.com/results',
            headers=spoofed_headers,
            params=payload)
        return response.text

    def parse_html(html: str) -> YoutubeSearchHit:
        query = PyQuery(html)
        match = query('a.yt-uix-tile-link')
        href = match.attrib("href")

        return YoutubeSearchHit(
            title=match.text(),
            url=f'http://www.youtube.com{href}')

    html = get_html(search_query)
    return parse_html(html)


class Player:

    def __init__(self) -> None:
        self.vlc_player = vlc.MediaPlayer()

    def play(self, song: str) -> None:
        # TODO Do we need to release the media that is currently playing before playing the next one?
        media = song_media(song)
        self.vlc_player.set_media(media)
        self.vlc_player.play()

    def pause(self) -> None:
        self.vlc_player.pause()

    def increase_volume(self) -> None:
        pass

    def decrease_volume(self) -> None:
        pass

    def release(self) -> None:
        self.vlc_player.release()

    def status(self) -> Dict[str, str]:
        return { # TODO Currently, a dummy implementation
            'volume': 'volume',
            'song': 'song'
        }

    def status_json(self) -> str:
        return json.dumps(self.status())


Releasable = TypeVar('Releasable', Player, vlc.MediaPlayer, vlc.Media)


@contextlib.contextmanager
def releasing(player: Releasable) -> Iterator[Releasable]:
    try:
        yield player
    finally:
        player.release()

