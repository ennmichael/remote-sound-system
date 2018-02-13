import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Decode
import Json.Encode
import Http


serverUrl =
  "http://localhost:8000"


type alias ServerStatus =
  { volume : String
  , song : String
  , state: String
  }


type Msg
  = UpdateSongInput String
  | PlaySong
  | ServerResponse (Result Http.Error ServerStatus)


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
    playPath =
      serverUrl ++ "/play/" ++ songTitle
  in
    Http.post playPath Http.emptyBody statusDecoder


statusRequest : Http.Request ServerStatus
statusRequest =
  Http.get (serverUrl ++ "/status") statusDecoder


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
  { volume = "-"
  , song = "-"
  , state = "-"
  }


errorServerStatus : ServerStatus
errorServerStatus = -- TODO How about: proper error handling
  { volume = "ERROR"
  , song = "ERROR"
  , state = "ERROR"
  }


update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
  case msg of
    UpdateSongInput newInput ->
      ( {model | songInput = newInput}
      , Cmd.none
      )

    PlaySong ->
      ( model
      , Http.send ServerResponse (playRequest model.songInput)
      )

    ServerResponse (Err err) ->
      ( {model | serverStatus = errorServerStatus}
      , Cmd.none
      )

    ServerResponse (Ok status) ->
      ( {model | serverStatus = status}
      , Cmd.none
      )


subscriptions : Model -> Sub msg
subscriptions model =
  Sub.none


view : Model -> Html Msg
view model =
  Html.div
    []
    [ Html.input
        [ Html.Events.onInput UpdateSongInput
        , Html.Attributes.placeholder "Song Name"
        ]
        []
    , Html.br [] []
    , Html.button
        [Html.Events.onClick PlaySong]
        [Html.text "Play"]
    , Html.br [] []
    , Html.br [] []
    , serverStatusView model.serverStatus
    ]


serverStatusView : ServerStatus -> Html Msg
serverStatusView serverStatus = -- TODO Make these align nicely.
  Html.div
    []
    [ Html.text ("Song: " ++ serverStatus.song)
    , Html.br [] []

    , Html.text ("Volume: " ++ serverStatus.volume)
    , Html.br [] []

    , Html.text ("State: " ++ serverStatus.state)
    ]

