import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Decode
import Json.Encode
import Http
import Time exposing (Time)


serverUrl =
  "http://localhost:8000"


type alias ServerStatus =
  { volume : String
  , song : String
  , state: String
  }


type Msg
  = UpdateSongInput String
  | UpdateStatus Time
  | ServerResponse (Result Http.Error ServerStatus)
  | PlaySong
  | IncraseVolume
  | DecreaseVolume
  | TogglePause


type alias Model = 
  { serverStatus : ServerStatus
  , songInput : String
  }
 

statusDecoder : Json.Decode.Decoder ServerStatus
statusDecoder =
  Json.Decode.map3
    ServerStatus
    (Json.Decode.field "volume" Json.Decode.string)
    (Json.Decode.field "song" Json.Decode.string)
    (Json.Decode.field "state" Json.Decode.string)


playRequest : String -> Http.Request ServerStatus
playRequest songTitle =
  let
    path =
      serverUrl ++ "/play/" ++ (Http.encodeUri songTitle)
  in
    serverPostRequest path


increaseVolumeRequest : Http.Request ServerStatus
increaseVolumeRequest =
  serverPostRequest "/increasevolume"


decreaseVolumeRequest : Http.Request ServerStatus
decreaseVolumeRequest =
  serverPostRequest "/decreasevolume"


togglePauseRequest : Http.Request ServerStatus
togglePauseRequest =
  serverPostRequest "/togglepause"


statusRequest : Http.Request ServerStatus
statusRequest =
  serverGetRequest "/status"


serverGetRequest : String -> Http.Request ServerStatus
serverGetRequest path =
  Http.get (serverUrl ++ path) statusDecoder


serverPostRequest : String -> Http.Request ServerStatus
serverPostRequest path =
  Http.post path Http.emptyBody statusDecoder


main =
  Html.program
    { init = init
    , update = update
    , subscriptions = subscriptions
    , view = view
    }


init : (Model, Cmd Msg)
init =
  (emptyModel, Cmd.none)


emptyModel : Model
emptyModel =
  { serverStatus = emptyServerStatus
  , songInput = ""
  }


emptyServerStatus : ServerStatus
emptyServerStatus =
  { volume = "0"
  , song = "-"
  , state = "-"
  }


errorServerStatus : ServerStatus
errorServerStatus =
  { volume = "ERROR"
  , song = "ERROR"
  , state = "ERROR"
  }


update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
  let
    sendRequest request =
      Http.send ServerResponse request
  in
    case msg of
      UpdateSongInput newInput ->
        ( {model | songInput = newInput}
        , Cmd.none
        )

      ServerResponse (Err err) ->
        ( {model | serverStatus = errorServerStatus}
        , Cmd.none
        )

      ServerResponse (Ok status) ->
        ( {model | serverStatus = status}
        , Cmd.none
        )

      UpdateStatus _ ->
        ( model
        , Http.send ServerResponse statusRequest
        )

      PlaySong ->
        ( model
        , sendRequest (playRequest model.songInput)
        )

      IncraseVolume ->
        ( model
        , sendRequest increaseVolumeRequest
        )

      DecreaseVolume ->
        ( model
        , sendRequest decreaseVolumeRequest
        )

      TogglePause ->
        ( model
        , sendRequest togglePauseRequest
        )


subscriptions : Model -> Sub Msg
subscriptions model =
  Time.every (5 * Time.second) UpdateStatus


view : Model -> Html Msg
view model =
  Html.div
    []
    [ Html.input
        [ Html.Events.onInput UpdateSongInput
        , Html.Attributes.placeholder "Song Name"
        ]
        []
    , simpleBr

    , playButton
    , simpleBr

    , togglePauseButton
    , simpleBr

    , volumeControl
    , simpleBr

    , serverStatusView model.serverStatus
    ]


serverStatusView : ServerStatus -> Html Msg
serverStatusView serverStatus =
  Html.div
    []
    [ Html.text ("Song: " ++ serverStatus.song)
    , simpleBr

    , Html.text ("Volume: " ++ serverStatus.volume)
    , simpleBr

    , Html.text ("State: " ++ serverStatus.state)
    ]


playButton : Html Msg
playButton =
  simpleHtmlButton PlaySong "Play"


increaseVolumeButton : Html Msg
increaseVolumeButton =
  simpleHtmlButton IncraseVolume "+"


decreaseVolumeButton : Html Msg
decreaseVolumeButton =
  simpleHtmlButton DecreaseVolume "-"


togglePauseButton : Html Msg
togglePauseButton =
  simpleHtmlButton TogglePause "Toggle Pause"


simpleHtmlButton : Msg -> String -> Html Msg
simpleHtmlButton msg text =
  Html.button
    [Html.Events.onClick msg]
    [Html.text text]


simpleBr : Html Msg
simpleBr =
  Html.br [] []


volumeControl : Html Msg
volumeControl =
  Html.div
    []
    [ Html.text "Volume Control: "
    , increaseVolumeButton
    , decreaseVolumeButton
    ]

