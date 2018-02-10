from typing import Optional, Iterator

import contextlib

import vlc
import pafy


def play_youtube_title(title: str) -> None:
    # If the video is cached, play the local video.
    # If the video is not cached, play the video from youtube.



def play_media(media: str) -> None:
    player = releasing(vlc.MediaPlayer(media))
    player.play()


@contextlib.contextmanager
def releasing(player: vlc.MediaPlayer) -> Iterator[vlc.MediaPlayer]:
    try:
        yield player
    finally:
        player.release()

