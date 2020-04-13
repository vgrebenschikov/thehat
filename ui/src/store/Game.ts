import {action, observable} from 'mobx';
import {User} from 'firebase';
import WebSocketConnection from "./WebSocketConnection";
import {GameState, PlayerState} from "./types";

export interface Player {
    name: string;
    uid: string;
}

export default class Game {
    @observable id: string;
    @observable connected: boolean = false;
    @observable serverGameId: string | null = null;

    @observable gameState: GameState = GameState.ST_CONFIG;
    @observable players: Player[] = [];
    @observable myState: PlayerState = PlayerState.ST_UNKNOWN;
    @observable gameNumWords: number | null = null;
    @observable tourNumber: number | null = null;
    @observable turnNumber: number | null = null;
    @observable explainer: string | null = null;
    @observable guesser: string | null = null;
    @observable timerStart: Date | null = null;
    @observable currentWord: string | null = null;
    @observable turnWords: string[] = [];

    private ws: WebSocketConnection;
    private readonly commands: {[k: string]: (data: any) => void};

    user: Player;

    constructor(name: string, user: User, ws: WebSocketConnection) {
        this.commands = {
            game: this.cmdGame,
            prepare: this.cmdPrepare,
            wait: this.cmdWait,
            tour: this.cmdTour,
            turn: this.cmdTurn,
            start: this.cmdStart,
            next: this.cmdNext,
            explained: this.cmdExplained,
            missed: this.cmdMissed,
            stop: this.cmdStop,
            finish: this.cmdFinish,
            error: this.cmdError,
        };
        this.id = name;
        this.ws = ws;
        this.ws.subscribeReceiver((data: any) => {this.commands[data?.cmd]?.(data);});
        this.user = { name: user.displayName || 'Unknown', uid: user.uid };
        this.connect();
    }

    connect = () => {
        this.ws.send({
            cmd: 'name',
            name: this.user.uid,
        });
    };

    @action
    sendWords(words: string[]) {
        this.ws.send({
            cmd: 'words',
            words: words,
        });
        this.myState = PlayerState.ST_READY;
    }

    sendPlay() {
        this.ws.send({
            cmd: 'play'
        });
    }


    @action.bound
    cmdGame (data: any) {
        this.serverGameId = data.id || null;
        this.gameNumWords = data.numwords || null;
        this.myState = PlayerState.ST_WORDS;
    };

    @action.bound
    cmdPrepare (data: any) {
        this.players = data.players.map((p: string) => ({name: p, uid: ''}));
    };

    @action.bound
    cmdWait (data: any) {
        this.gameState = GameState.ST_CONFIG;
    };

    @action.bound
    cmdTour (data: any) {
        this.tourNumber = data.tour || null;
    };

    @action.bound
    cmdTurn (data: any) {
        this.turnNumber = data.turn || null;
        this.explainer = data.explain || null;
        this.guesser = data.guess || null;
        if (this.explainer === this.user?.name) {
            this.myState = PlayerState.ST_PREPARE_EXPLAIN;
        } else if (this.guesser === this.user?.name) {
            this.myState = PlayerState.ST_PREPARE_GUESS;
        } else {
            this.myState = PlayerState.ST_READY;
        }
        this.gameState = GameState.ST_TURNSTART;
    };

    @action.bound
    cmdStart (data: any) {
        this.gameState = GameState.ST_TURN;
        if (this.myState === PlayerState.ST_PREPARE_GUESS) {
            this.myState = PlayerState.ST_GUESS;
        }
        if (this.myState === PlayerState.ST_PREPARE_EXPLAIN) {
            this.myState = PlayerState.ST_EXPLAIN;
        }
        this.timerStart = new Date();
        this.turnWords = [];
    };

    @action.bound
    cmdNext (data: any) {
        this.currentWord = data.word;
    };

    @action.bound
    cmdExplained (data: any) {
        this.turnWords.push(data.word)
    };

    @action.bound
    cmdMissed (data: any) {

    };

    @action.bound
    cmdStop (data: any) {
        this.gameState = GameState.ST_AFTERTURN;
    };

    @action.bound
    cmdFinish (data: any) {
        this.gameState = GameState.ST_FINISH;
    };

    @action.bound
    cmdError (data: any) {

    };
}