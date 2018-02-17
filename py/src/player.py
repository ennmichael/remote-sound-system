#!/usr/bin/env python3


# TODO Rename this file to youtube_player.py


from typing import Iterator, NamedTuple, TypeVar, Generic, Dict
import contextlib
import collections
import pathlib
import json
import subprocess
import urllib.parse

import vlc
import pafy
from pyquery import PyQuery


class ChromeError(BaseException):

    pass


def load_webpage(url: str) -> str:
    args = [
        'google-chrome',
        '--headless',
        '--dump-dom',
        url
    ]

    process = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    if process.returncode != 0:
        raise ChromeError(process.stderr)
    else:
        return process.stdout or ''


class SongNotCached(BaseException):

    pass


class SongMedia(NamedTuple):

    title: str
    vlc_media: vlc.Media


def song_media(song: str) -> SongMedia:
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


class YoutubeVideo(NamedTuple):

    title: str
    url: str


def find_on_youtube(search_query: str) -> YoutubeVideo:
    def get_html(search_query: str) -> str:
        search_query = urllib.parse.quote(search_query)
        url = f'https://www.youtube.com/results?search_query={search_query}'
        return load_webpage(url)

    def parse_html(html: str) -> YoutubeVideo:
        query = PyQuery(html)
        match = query('a#video-title').eq(0)
        href = match.attr("href")
        url = f'https://www.youtube.com/{href}'# TODO This ought to be a separate function
        video = pafy.new(url)

        return YoutubeVideo(
            title=video.title,
            url=video.getbestaudio().url)

    html = get_html(search_query)
    return parse_html(html)


class YoutubePlayer:

    DEFAULT_VOLUME_DELTA = 10

    def __init__(self) -> None:
        self.vlc_player = vlc.MediaPlayer()
        self.song = ''

    def play(self, song: str) -> None:
        title, media = song_media(song)

        import pdb; pdb.set_trace()

        self.song = title
        self.play_vlc_media(media)

    def play_vlc_media(self, media: vlc.Media) -> None:
        self.vlc_player.set_media(media)
        self.vlc_player.play()

    def toggle_pause(self) -> None:
        self.vlc_player.pause()

    def is_paused(self) -> bool:
        return bool(self.vlc_player.get_state() == vlc.State.Paused)

    def is_playing(self) -> bool:
        return bool(self.vlc_player.get_state() == vlc.State.Playing)

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
        return int(self.vlc_player.audio_get_volume())

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


Releasable = TypeVar('Releasable', YoutubePlayer, vlc.MediaPlayer, vlc.Media)


@contextlib.contextmanager
def releasing(releasable: Releasable) -> Iterator[Releasable]:
    try:
        yield releasable
    finally:
        releasable.release()

