#!/usr/bin/env python3


from typing import NamedTuple, Dict, Optional
import pathlib
import json
import subprocess
import urllib.parse
import io

import vlc
import pafy
from pyquery import PyQuery


class ChromeError(BaseException):

    pass


def load_webpage(url: str) -> str:
    args = [
        'chromium-browser',
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


def download_url(url: str, output_path: str) -> None:
    touch(output_path)

    args = [
        'wget',
        '-b',
        '-O', output_path,
        '-t', '1',
        url
    ]

    subprocess.run(args, stdout=subprocess.PIPE)


def touch(path: str) -> None:
    io.open(path, 'a').close()


class SongNotCached(BaseException):

    pass


class SongMedia(NamedTuple):

    title: str
    vlc_media: vlc.Media


def file_exists(path: str) -> bool:
    return pathlib.Path(path).is_file()


class YoutubeVideo(NamedTuple):

    title: str
    url: str


def find_on_youtube(search_query: str) -> YoutubeVideo:
    def get_html(search_query: str) -> str:
        search_query = urllib.parse.quote(search_query)
        url = f'https://www.youtube.com/results?search_query={search_query}'
        return load_webpage(url)

    def top_video_url(html: str) -> str:
        query = PyQuery(html)
        match = query('a#video-title').eq(0)
        href = match.attr("href")
        return f'https://www.youtube.com/{href}'

    def parse_html(html: str) -> YoutubeVideo:
        url = top_video_url(html)
        video = pafy.new(url)
        return YoutubeVideo(
            title=video.title,
            url=video.getbestaudio().url)

    html = get_html(search_query)
    return parse_html(html)


class YoutubePlayer:

    DEFAULT_VOLUME_DELTA = 10

    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        self.vlc_player = vlc.MediaPlayer()
        self.song = ''
        self.set_volume(100)

    def play(self, song: str) -> None:
        title, media = self.song_media(song)
        self.song = title
        self.play_vlc_media(media)

    def song_media(self, song: str) -> vlc.Media:
        def cached_song_media(path: str) -> Optional[vlc.Media]:
            if not file_exists(path):
                return None
            return vlc.Media(path)

        def online_song_media(url: str) -> vlc.Media:
            return vlc.Media(url)

        # !!!
        # TODO This function is incomplete, and the caching functionality doesn't work
        # !!!

        title, url = find_on_youtube(song)
        online_media = online_song_media(url)
        return SongMedia(title, online_media) # TODO This is a premature return statement

        cached_song_path = f'{self.database_path}/{title}'
        cached_media = cached_song_media(cached_song_path)

        if cached_media: 
            return SongMedia(title, cached_media)
        else:
            online_media = online_song_media(url)
            download_url(url, cached_song_path)
            return SongMedia(title, online_media)

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
            self.vlc_player.audio_set_volume(volume)

    def volume(self) -> int:
        return int(self.vlc_player.audio_get_volume())

    def close(self) -> None:
        self.vlc_player.release()

    def status(self) -> Dict[str, str]:
        def state_str() -> str:
            if self.is_playing():
                return 'playing'
            elif self.is_paused():
                return 'paused'
            else:
                return 'unknown'

        def song_str() -> str:
            if self.is_playing() or self.is_paused():
                return self.song
            else:
                return ''

        return {
            'volume': str(self.volume()),
            'song': song_str(),
            'state': state_str()
        }

    def status_json(self) -> str:
        return json.dumps(self.status())


