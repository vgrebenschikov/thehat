# thehat
The Hat (Shlyapa) online game
* [Game overview](https://ru.wikipedia.org/wiki/Шляпа_(игра))
  - caution: English page attached to Russian page above belongs to other similar game
  - this game is about three-tour variant
# Terms 
- **Player** - one player of game 
    - **Player who Explains** - a player in pair who explain words to other player in pair
    - **Player who Guesses** - a player in pair who guesses words words
- **Words** - set of unique words provided by one player 
- **Tour** - part of game with fixed rule-set
    - First Tour - Explain words with **unlimited** other words and gestures
    - Second Tour - Explain words with only **one** other word and gestures
    - Third Tour - Explain words with **no** other words and gestures
- **Turn** - part of the game when selected pair explains words in limited time-frame
- **Round** - complete set of **Turns** when all combination of players acted

# Technology Stack 
* Backend
  * python3
  * aiohttp
  * WebSockets to communicate with frontend 
* Frontend 
  * typescript
  * react
  * mobx
  * material-ui
# How to Run
## Backend 
Running server for development 
```bash
$ python app.py
======== Running on http://0.0.0.0:8088 ========
(Press CTRL+C to quit)
[L:30]# DEBUG    [12-04-2020 01:06:14]  websocket new connection
[L:38]# DEBUG    [12-04-2020 01:06:18]  websocket message received: 1: {"cmd": "name", "name": "vova"}
[L:58]# DEBUG    [12-04-2020 01:06:18]  Received command name
[L:23]# DEBUG    [12-04-2020 01:06:18]  user vova logged in as 4482238864
...
```
How to test WebSocket connection:
```bash
$ websocat --exit-on-eof ws://127.0.0.1:8088/ws
{"cmd": "name", "name": "vova"}
{"cmd": "game", "id": "7b5e87e5-39d4-481b-bac1-b4bc69e24fc0", "numwords": 6}
{"cmd": "words", "words": [ "a1", "a2", "a3", "a4", "a5" ]}
{"cmd": "prepare", "players": ["vova", "leo"]}
{"cmd": "play"}
{"cmd": "tour", "tour": 0}
{"cmd": "play"}
```

## Frontend (development)

You need to supply a set of firebase credentials, placing the config file in `ui/src/firebase-config.ts`. The contents of this file is secret so it is not included in this git.

```bash
$ cd ui
$ yarn install
$ yarn start
```
(this will open a browser to http://localhost:3000 and connect to the backend running on localhost:8088 