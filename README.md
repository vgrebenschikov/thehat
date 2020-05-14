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
  * python-3.8
  * aiohttp
  * WebSockets to communicate with frontend 
* Frontend 
  * typescript
  * react
  * mobx
  * material-ui

# How to Run

## Requirements
  * python 3.8
  * nodejs + yarn
  * nginx

## Backend 

Running server for development 
```bash
$ pip install -r requirements.txt
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

Running production service under gunicorn:
```bash
$ gunicorn --bind 0.0.0.0:8088 --worker-class aiohttp.worker.GunicornWebWorker --workers 1 --threads 8 app:app
```

## How to run tests suite
```bash
$ pip install -r test-requirements.txt
$ pytest tests --cov=. --cov-report=xml --cov-report=term-missing --no-cov-on-fail
```

## Frontend (development)

You need to supply a set of firebase credentials, placing the config file in `ui/src/firebase-config.ts`. The contents of this file is secret so it is not included in this git.

Running frontend for development purposes
```bash
$ cd ui
$ yarn install
$ yarn start
```
(this will open a browser to http://localhost:3000 and connect to the backend running on localhost:8088 

Generate frontend static folder
```bash
$ cd ui
$ yarn install
$ yarn build
```
Then put build/ folder under site root

## Example of nginx config to for hat server
# Hat Game server
Setup nginx to run hat server with following config:

```
upstream back {
	server 127.0.0.1:8088 max_conns=512;
}

server {

	root /usr/local/www/thehat;
	server_name hat.example.com;

	location /ws {
		allow all;

		proxy_pass http://back$request_uri;

      		proxy_http_version 1.1;
      		proxy_set_header Upgrade $http_upgrade;
      		proxy_set_header Connection "upgrade";

		proxy_read_timeout 86400;
		proxy_send_timeout 86400;

		proxy_set_header Host		    $host;
		proxy_set_header X-Real-IP          $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

	}

	location /games {
		allow all;

		proxy_pass http://back$request_uri;
		proxy_http_version 1.1;

		proxy_set_header X-Real-IP          $remote_addr;
		proxy_set_header X-Forwarded-For    $proxy_add_x_forwarded_for;
		proxy_set_header Host               $host;
	}

    location / {
            allow all;
            root /usr/local/www/thehat;

            try_files $uri /$uri
            try_files ''  /index.html;
    }

    listen 80;
    listen [::]:80;

    listen [::]:443 ssl; # managed by Certbot
    listen 443 ssl; # managed by Certbot
    ssl_certificate /usr/local/etc/letsencrypt/live/hat.example.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /usr/local/etc/letsencrypt/live/hat.example.com/privkey.pem; # managed by Certbot
    include /usr/local/etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /usr/local/etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

}
```