import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Decode
import Json.Encode
import Http


serverUrl =
  "localhost:8000"


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
    body =
      Http.stringBody
        "application/json" 
        (Json.Encode.encode 0 valueToEncode)

    valueToEncode =
      Json.Encode.object
        [("play", Json.Encode.string songTitle)
        ]
  in
    Http.post serverUrl body statusDecoder


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

    ServerResponse response -> -- TODO We should have *some* error handling here
      ( model
      , Cmd.none
      )


subscriptions : Model -> Sub msg
subscriptions model =
  Sub.none


serverStatusForHumans : ServerStatus -> String
serverStatusForHumans serverStatus =
  "Song: " ++ serverStatus.song ++ "\n" ++
  "Volume: " ++ serverStatus.volume ++ "\n" ++
  "State: " ++ serverStatus.state ++ "\n"


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
    ]

