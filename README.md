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
======== Running on http://0.0.0.0:8080 ========
(Press CTRL+C to quit)
[L:30]# DEBUG    [12-04-2020 01:06:14]  websocket new connection
[L:38]# DEBUG    [12-04-2020 01:06:18]  websocket message received: 1: {"cmd": "name", "name": "vova"}
[L:58]# DEBUG    [12-04-2020 01:06:18]  Received command name
[L:23]# DEBUG    [12-04-2020 01:06:18]  user vova logged in as 4482238864
...
```