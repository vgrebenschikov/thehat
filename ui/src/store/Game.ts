import {action, observable} from 'mobx';
import {User} from 'firebase';
import WebSocketConnection from "./WebSocketConnection";
import {GameState, PlayerRole, PlayerState} from "./types";

export interface Player {
    name: string;
    uid: string;
    done: boolean;
}

export default class Game {
    @observable id: string;
    @observable connected: boolean = false;
    @observable serverGameId: string | null = null;

    @observable gameState: GameState = GameState.SETUP;
    @observable players: Player[] = [];
    @observable myState: PlayerState = PlayerState.UNKNOWN;
    @observable myRole: PlayerRole = PlayerRole.WATCHER;
    @observable gameNumWords: number | null = null;
    @observable turnTime: number | null = null;
    @observable tourNumber: number | null = null;
    @observable turnNumber: number | null = null;
    @observable explainer: string | null = null;
    @observable guesser: string | null = null;
    @observable timerStart: Date | null = null;
    @observable timeLeft: number | null = null;
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
        this.ws.subscribeReceiver(this.onMessageReceived);
        this.user = { name: user.displayName || 'Unknown', uid: user.uid, done: false };
        setInterval(this.updateTimeLeft, 1000);
        this.connect();
    }

    onMessageReceived = (data: any) => {
        if (data === null) {
            this.connect();
        } else {
            this.commands[data?.cmd]?.(data);
        }
    };

    @action.bound
    updateTimeLeft() {
        if (!this.timerStart) {
            this.timeLeft = null;
            return;
        }
        const timePassed = (new Date().getTime() - this.timerStart.getTime());
        this.timeLeft = Math.ceil((this.turnTime! - timePassed / 1000));
    }

    connect = () => {
        this.ws.send({
            cmd: 'name',
            name: this.user.name,
        });
    };

    @action.bound
    sendWords(words: string[]) {
        this.ws.send({
            cmd: 'words',
            words: words,
        });
        this.myState = PlayerState.WAIT;
    }

    @action.bound
    sendPlay() {
        this.ws.send({
            cmd: 'play'
        });
    }

    @action.bound
    sendReady() {
        this.ws.send({
            cmd: 'ready'
        });
        this.myState = PlayerState.READY;
    }

    @action.bound
    cmdGame (data: any) {
        this.serverGameId = data.id || null;
        this.gameNumWords = data.numwords || null;
        this.turnTime = data.timer || null;
        this.myState = PlayerState.WORDS;  // TODO: this should come in the 'game' command
        this.gameState = GameState.SETUP;  // TODO: this should come in the 'game' command
    };

    @action.bound
    cmdPrepare (data: any) {
        this.players = Object.entries(data.players).map(([p, v]) => ({name: p, uid: '', done: v !== 0}));
    };

    @action.bound
    cmdWait (data: any) {
        this.gameState = GameState.SETUP;
    };

    @action.bound
    cmdTour (data: any) {
        this.tourNumber = data.tour || null;
        this.gameState = GameState.PLAY;
    };

    @action.bound
    cmdTurn (data: any) {
        this.turnNumber = data.turn || null;
        this.explainer = data.explain || null;
        this.guesser = data.guess || null;
        this.gameState = GameState.PREP_TURN;
        this.timerStart = null;
        if (this.explainer === this.user?.name) {
            this.myState = PlayerState.BEGIN;
            this.myRole = PlayerRole.EXPLAINER;
        } else if (this.guesser === this.user?.name) {
            this.myState = PlayerState.BEGIN;
            this.myRole = PlayerRole.GUESSER;
        } else {
            this.myState = PlayerState.WAIT;
            this.myRole = PlayerRole.WATCHER;
        }
    };

    @action.bound
    cmdStart (data: any) {
        this.gameState = GameState.TURN;
        if (this.myRole !== PlayerRole.WATCHER) {
            this.myState = PlayerState.PLAY;
        }
        this.timerStart = new Date();
        this.updateTimeLeft();
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
        this.myState = PlayerState.LAST_ANSWER;
    };

    @action.bound
    cmdFinish (data: any) {
        this.gameState = GameState.FINISH;
        this.timerStart = null;
    };

    @action.bound
    cmdError (data: any) {

    };
}