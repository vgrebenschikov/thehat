export enum GameState {
  ST_CONFIG = "ST_CONFIG",  // Game doesn't start. Players log in.
  ST_PLAY = "ST_PLAY",      // Game started.
  ST_TURNSTART = "ST_TURNSTART", // Explainer/guesser selected, waiting for them to be ready.
  ST_TURN = "ST_TURN", // Timer is running!
  ST_AFTERTURN = "ST_AFTERTURN", // Time us up, prepare for next turn.
  ST_FINISH = "ST_FINISH",  // Game finished.
}

export enum PlayerState {
  ST_UNKNOWN = "ST_UNKNOWN",  // Player unknown (haven't logged in yet).
  ST_WORDS = "ST_WORDS",      // Enter words.
  ST_READY = "ST_READY",      // In play, just look, waits for their turn.
  ST_EXPLAIN = "ST_EXPLAIN",  // Explain word.
  ST_PREPARE_EXPLAIN = "ST_PREPARE_EXPLAIN", // Preparing for explain. Not ready yet.
  ST_GUESS = "ST_GUESS",      // Guess word.
  ST_PREPARE_GUESS = "ST_PREPARE_GUESS", // Preparing for guess. Not ready yet.
  ST_FINISH = "ST_FINISH",    // Game finished.
}

