import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Decode
import Json.Encode
import Http
import Time exposing (Time)


serverUrl =
  "http://192.168.45.50:8000"

type alias ServerStatus =
  { volume : String
  , currentSong : String
  , state: String
  , songQueue: List String
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
  Result
    Http.Error
    { serverStatus : ServerStatus
    , songInput : String
    }
 

statusDecoder : Json.Decode.Decoder ServerStatus
statusDecoder =
  Json.Decode.map4
    ServerStatus
    (Json.Decode.field "volume" Json.Decode.string)
    (Json.Decode.field "currentSong" Json.Decode.string)
    (Json.Decode.field "state" Json.Decode.string)
    (Json.Decode.field "songQueue" (Json.Decode.list Json.Decode.string))


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
  Ok
    { serverStatus = emptyServerStatus
    , songInput = ""
    }


emptyServerStatus : ServerStatus
emptyServerStatus =
  { volume = "100"
  , currentSong = ""
  , state = ""
  , songQueue = []
  }


subscriptions : Model -> Sub Msg
subscriptions model =
  Time.every Time.second UpdateStatus


update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
  let
    sendRequest request =
      Http.send ServerResponse request

    updateOkModel model =
      case msg of
        UpdateSongInput newInput ->
          ( Ok {model | songInput = newInput}
          , Cmd.none
          )

        ServerResponse (Err err) ->
          ( Err err
          , Cmd.none
          )

        ServerResponse (Ok status) ->
          ( Ok {model | serverStatus = status}
          , Cmd.none
          )

        UpdateStatus _ ->
          ( Ok model
          , Http.send ServerResponse statusRequest
          )

        PlaySong ->
          ( Ok model
          , sendRequest (playRequest model.songInput)
          )

        IncraseVolume ->
          ( Ok model
          , sendRequest increaseVolumeRequest
          )

        DecreaseVolume ->
          ( Ok model
          , sendRequest decreaseVolumeRequest
          )

        TogglePause ->
          ( Ok model
          , sendRequest togglePauseRequest
          )
  in
    case model of
      Err _ ->
        ( model
        , Cmd.none
        )

      Ok model ->
        updateOkModel model


view : Model -> Html Msg
view model =
  case model of
    Ok {serverStatus} ->
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

        , togglePauseButton serverStatus.state
        , simpleBr

        , volumeControl serverStatus.volume

        , currentSongDiv serverStatus.currentSong
        , simpleBr

        , songQueueDiv serverStatus.songQueue
        ]

    Err err ->
      errorDiv err


currentSongDiv : String -> Html Msg
currentSongDiv currentSong =
  if currentSong == "" then
    Html.div [] []
  else
    Html.div
      []
      [ Html.text ("Current Song: " ++ currentSong)
      ]


songQueueDiv : List String -> Html Msg
songQueueDiv songQueue =
  let
    subdivs =
      List.map songDiv (List.reverse songQueue)
  in
    if songQueue == [] then
      Html.div [] []
    else
      Html.div
        []
        ([Html.text "Song Queue: ", simpleBr] ++ subdivs)


songDiv : String -> Html Msg
songDiv song =
    Html.div
      []
      [Html.text song, simpleBr]


playButton : Html Msg
playButton =
  simpleHtmlButton PlaySong "Play"


increaseVolumeButton : Html Msg
increaseVolumeButton =
  simpleHtmlButton IncraseVolume "+"


decreaseVolumeButton : Html Msg
decreaseVolumeButton =
  simpleHtmlButton DecreaseVolume "-"


togglePauseButton : String -> Html Msg
togglePauseButton state =
  case state of
    "playing" ->
      Html.div [] [simpleHtmlButton TogglePause "Pause"]

    "paused" ->
      Html.div [] [simpleHtmlButton TogglePause "Continue"]

    _ ->
      Html.div [] []


simpleHtmlButton : Msg -> String -> Html Msg
simpleHtmlButton msg text =
  Html.button
    [Html.Events.onClick msg]
    [Html.text text]


simpleBr : Html Msg
simpleBr =
  Html.br [] []


volumeControl : String -> Html Msg
volumeControl currentVolume =
  Html.div
    []
    [ Html.text ("Volume: " ++ currentVolume)
    , increaseVolumeButton
    , decreaseVolumeButton
    ]


errorDiv : Http.Error -> Html Msg
errorDiv err =
  let
    errorMessage =
      case err of
        Http.BadUrl url ->
          "Bad url: " ++ url

        Http.Timeout ->
          "Timed out"

        Http.NetworkError ->
          "Network error"

        Http.BadStatus _ ->
          "Bad status code"
      
        Http.BadPayload _ _ ->
          "Developer error"
  in
    Html.div
      [Html.Attributes.style [("color", "red")]]
      [Html.text ("ERROR: " ++ errorMessage ++ ".")]

