export enum GameState {
  SETUP = 'setup',
  PLAY = 'play',

  PREP_TURN = 'prep_turn',
  TURN = 'turn',

  FINISH = 'finish',
}

export enum PlayerState {
  UNKNOWN = 'unknown',         // Just connected - unknown
  WORDS = 'words',             // Waiting for words from player
  WAIT = 'wait',               // Waiting for his move
  BEGIN = 'begin',             // Begin of turn, player selected in pair
  READY = 'ready',             // Player ready to start turn
  PLAY = 'play',               // Playing (timer runs)
  LAST_ANSWER = 'lastanswer',  // Waiting for last explanation results (time is out)
  FINISH = 'finish',           // Finishing turn
}

export enum PlayerRole {
  WATCHER = 'watcher',
  EXPLAINER = 'explainer',
  GUESSER = 'guesser',
}