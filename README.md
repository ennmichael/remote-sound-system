# Remote sound system

Communication between the server and the client is done using JSON.
Client would POST:

```
{
    playSong: "title"
}
```

And the song would play.
Such POST requests made to path `/`, as well as GET requests made to path `/status` will generate responses like this one:

```
{
    volume: "0-100",
    song: "song title"
}
```

GET requests to `/` will serve the index file.
Requests made to any other path should return a 404. This is not implemented yet. Currently, they might crash the server.

# Dependencies

```
sudo apt-get install -y youtube-dl libvlc-dev vlc wget
python3.6 -m pip install vlc
python3.6 -m pip install pafy
python3.6 -m pip install pyquery
```

Also, we use headless chrome, so you need chromium v59 at least.

# Running the server

The server should be started from the root directory. 

```
cd path-to/remote-sound-system
./server.sh
```

The `db` directory in the root directory will act as the song database. This is currently not configurable, but it probably should be.

