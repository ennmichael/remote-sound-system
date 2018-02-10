from typing import Optional


import vlc
import contextlib


class VLCPlayer(contextlib.AbstractContextManager):

    def __init__(self) -> None:
        self.libvlc = vlc.libvlc_new()

    def free(self) -> None:
        vlc.libvlc_release(self.libvlc)

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.free()

    def play_local_media(self, filename: str) -> None:
        media = self.local_media(filename)
        self.play_media(media)

    def play_network_media(self, url: str) -> None:
        media = self.network_media(url)
        self.play_media(media)

    def local_media(self, filename: str):
        pass

    def network_media(self, url: str):
        pass

    def play_media(self, media):
        pass


class YoutubePlayer:

    def __init__(self):
        self.vlc_player = VLCPlayer()

