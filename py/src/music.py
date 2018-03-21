#!/usr/bin/env python3


from typing import NamedTuple, Dict, Optional, List, Callable, Any
import pathlib
import subprocess
import urllib.parse
import io
import os

import vlc
import pafy
import io
from pyquery import PyQuery


class SubprocessError(BaseException):

    pass


def collapse_whitespace(s: str) -> str:
    return ' '.join(s.split())


def run_safely(*subprocess_args: str, background: bool=False) -> str:
    process = subprocess.run(
        subprocess_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags = subprocess.CREATE_NEW_CONSOLE if background else 0)

    if process.returncode != 0:
        raise SubprocessError(process.stderr)
    else:
        return process.stdout or ''


def touch(path: str) -> None:
    io.open(path, 'a').close()


def load_webpage(url: str) -> str:
    return run_safely(
        'chromium-browser',
        '--headless',
        '--dump-dom',
        url)


def download_url(url: str, output_path: str) -> None:
    os.system(f'./py/src/download.py "{url}" "{output_path}" &')


def file_exists(path: str) -> bool:
    return pathlib.Path(path).is_file()


def find_on_youtube(search_query: str) -> str:
    def get_html(search_query: str) -> str:
        search_query = urllib.parse.quote(search_query)
        url = f'https://www.youtube.com/results?search_query={search_query}'
        return load_webpage(url)

    def top_video_url(html: str) -> str:
        query = PyQuery(html)
        match = query('a#video-title').eq(0)
        href = match.attr("href")
        return f'https://www.youtube.com{href}'

    def direct_audio_url(video_url: str) -> str:
        video = pafy.new(video_url)
        audio = video.getbestaudio()
        return str(audio.url)

    html = get_html(search_query)
    video_url = top_video_url(html)
    return direct_audio_url(video_url)


class YoutubePlayer:

    DEFAULT_VOLUME_DELTA = 10

    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        self.vlc_player = vlc.MediaPlayer()
        self.current_song = ''
        self.set_volume(100)

    def play(self, song: str) -> None:
        if self.song_is_cached(song):
            self.play_from_cache(song)
        else:
            url = find_on_youtube(song)
            self.play_online(url)
            self.cache_song(song, url)
        self.current_song = song

    def song_is_cached(self, song: str) -> bool:
        return file_exists(self.cached_song_path(song))

    def cache_song(self, song: str, url: str) -> None:
        download_url(url, self.cached_song_path(song))

    def cache_if_needed(self, song: str) -> None:
        if not self.song_is_cached(song):
            url = find_on_youtube(song)
            self.cache_song(song, url)

    def play_from_cache(self, song: str) -> None:
        self.play_vlc_media(self.cached_song_media(song))

    def play_online(self, url: str) -> None:
        media = vlc.Media(url)
        self.play_vlc_media(media)

    def cached_song_path(self, song: str) -> str:
        return f'{self.database_path}/{song}'

    def cached_song_media(self, song: str) -> vlc.Media:
        return vlc.Media(self.cached_song_path(song))

    def play_vlc_media(self, media: vlc.Media) -> None:
        self.vlc_player.set_media(media)
        self.vlc_player.play()

    def toggle_pause(self) -> None:
        self.vlc_player.pause()

    def is_paused(self) -> bool:
        return bool(self.vlc_player.get_state() == vlc.State.Paused)

    def is_playing(self) -> bool:
        return bool(self.vlc_player.get_state() == vlc.State.Playing)

    def playback_done(self) -> bool:
        return bool(self.vlc_player.get_state() == vlc.State.NothingSpecial or
                    self.vlc_player.get_state() == vlc.State.Ended)

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

    def status(self) -> Dict[str, Any]:
        def state_str() -> str:
            if self.is_playing():
                return 'playing'
            elif self.is_paused():
                return 'paused'
            else:
                return 'unknown'

        def current_song_str() -> str:
            if self.is_playing() or self.is_paused():
                return self.current_song
            else:
                return ''

        return {
            'volume': str(self.volume()),
            'currentSong': current_song_str(),
            'state': state_str()
        }


class SongLoop:

    def __init__(self, player: YoutubePlayer) -> None:
        self.player = player
        self.song_queue: List[str] = []
    
    def add_song(self, song: str) -> None:
        if song:
            song = collapse_whitespace(song).lower()
            if self.player.playback_done():
                self.player.play(song)
            else:
                self.song_queue.insert(0, song)
                self.player.cache_if_needed(song)

    def update(self) -> None:
        if self.player.playback_done() and self.song_queue:
            next_song = self.song_queue.pop()
            self.player.play(next_song)

