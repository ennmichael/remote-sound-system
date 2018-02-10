Communication between the server and the client is done using json.
Client:

```
{
    request: "requestType requestParameters"
}
```

`"requestType"` can be `"status"`, in which case there's no parameters. It can also be `"play"`, in which case the parameter is the song name.
Server will only resond with the status like:

```
{
    volume: "0-100",
    song: "song title"
}
```

When the client requires a new song, that's a POST request. Status updates are GET requests.
Status updates are made to `server_url/status`.

