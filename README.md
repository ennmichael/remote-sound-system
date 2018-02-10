# Remote sound system

Communication between the server and the client is done using json.
Client:

```
{
    requestType: "...",
    requestParameter: "..."
}
```

`"requestType"` can be `"status"`, in which case there's no parameters (requestParameter is an empty string). It can also be `"play"`, in which case the parameter is the song name.
Server will only resond with the status like:

```
{
    volume: "0-100",
    song: "song title"
}
```

When the client requires a new song, that's a POST request. Status update requests are GET requests.
Status updates are made to `server_url/status`.


# Dependencies

```
sudo apt install -y youtube-dl
python3.6 -m pip install vlc
python3.6 -m pip install vlc
```

