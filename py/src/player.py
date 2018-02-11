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


class SongMedia(NamedTuple):

    title: str
    vlc_media: vlc.Media


def song_media(song: str) -> SongMedia
    title, url = find_on_youtube(song)

    try:
        return SongMedia(title, cached_song_media(title))
    except SongNotCached:
        return SongMedia(title, online_song_media(url))


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

    DEFAULT_VOLUME_DELTA = 10

    def __init__(self) -> None:
        self.vlc_player = vlc.MediaPlayer()
        self.song: Optional[str] = None

    def play(self, song: str) -> None:
        media = song_media(song)
        self.vlc_player.set_media(media)
        self.vlc_player.play()

    def toggle_pause(self) -> None:
        self.vlc_player.pause()

    def is_paused(self) -> bool:
        return self.vlc_player.get_state() == vlc.State.Paused

    def is_playing(self) -> bool:
        return self.vlc_player.get_state() == vlc.State.Playing

    def increase_volume(self, delta: int=DEFAULT_VOLUME_DELTA) -> None:
        self.set_volume(self.volume() + delta)

    def decrease_volume(self, delta: int=DEFAULT_VOLUME_DELTA) -> None:
        self.set_volume(self.volume() - delta)

    def set_volume(self, volume: int) -> None:
        if volume < 0:
            self.set_volume(0)
        elif volume > 100:
            self.set_volume(100)
        else:
            self.set_volume(volume)

    def volume(self) -> int:
        return self.vlc_player.audio_get_volume()

    def release(self) -> None:
        self.vlc_player.release()

    def status(self) -> Dict[str, str]:
        def state_str() -> str:
            if self.is_playing():
                return 'playing'
            elif self.is_paused():
                return 'paused'
            else:
                return '-'

        def song_str() -> str:
            if self.is_playing() or self.is_paused():
                return self.song
            else:
                return '-'

        return {
            'volume': str(self.volume()),
            'song': song_str(),
            'state': state_str()
        }

    def status_json(self) -> str:
        return json.dumps(self.status())


Releasable = TypeVar('Releasable', Player, vlc.MediaPlayer, vlc.Media)


@contextlib.contextmanager
def releasing(releasable: Releasable) -> Iterator[Releasable]:
    try:
        yield releasable
    finally:
        releasable.release()

