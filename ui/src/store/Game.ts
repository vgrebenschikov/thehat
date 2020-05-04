import {action, computed, observable} from 'mobx';
import UIfx from 'uifx';
import {User} from 'firebase';
import WebSocketConnection, {ConnectionStatus} from "./WebSocketConnection";
import {GameState, PlayerRole, PlayerState} from "./types";
import UIStore from './UIStore';

const startBell = new UIfx('/start.mp3');
const timeoutBell = new UIfx('/timesup2.mp3');

export interface Player {
    name: string;
    words: number;
    avatar: string | undefined;
}

export type PlayerMap = { [player: string]: Player };

export type TourResults = { [player: string]: number };

export interface GameResults {
    score: {[player: string]: {
            total: number;
            explained: number;
            guessed: number;
    }};

    explained: TourResults[];
    guessed: TourResults[];
}

export default class Game {
    @observable id: string;
    @observable connected: boolean = false;
    @observable gameName: string | null = null;
    @observable ws: WebSocketConnection;

    @observable gameState: GameState = GameState.SETUP;
    @observable players: PlayerMap = {};
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
    @observable results: GameResults | null = null;

    private readonly commands: {[k: string]: (data: any) => void};
    private uistore: UIStore;

    user: Player;

    constructor(name: string, user: User, uistore: UIStore) {
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
        this.uistore = uistore;
        this.ws = new WebSocketConnection(name);
        this.ws.reconnect();
        this.ws.subscribeReceiver(this.onMessageReceived);
        this.user = {
            name: user.displayName || 'Unknown',
            words: 0,
            avatar: user.photoURL || undefined,
        };
        setInterval(this.updateTimeLeft, 1000);
        if (this.ws.connectionStatus === ConnectionStatus.Established) {
            // Otherwise, connect() will be called when connection is established.
            this.connect();
        }
    }

    @computed get playerList(): Player[] {
        return Object.getOwnPropertyNames(this.players)
          .sort()
          .map((p) => this.players[p]);
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
            avatar: this.user.avatar,
        });
        this.tourNumber = null;
        this.turnNumber = null;
        this.results = null;
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
    sendGuessed(correctly: boolean) {
        this.ws.send({
            cmd: 'guessed',
            guessed: correctly,
        });
        if (this.myState === PlayerState.LAST_ANSWER) {
            this.myState = PlayerState.FINISH;
        }
    }

    @action.bound
    sendRestart() {
        this.ws.send({
            cmd: 'restart',
        });
        this.myState = PlayerState.UNKNOWN;
        this.gameState = GameState.SETUP;
    }

    @action.bound
    cmdGame (data: any) {
        this.gameName = data.name || 'Неизвестная игра';
        this.gameNumWords = data.numwords || null;
        this.turnTime = data.timer || null;
        this.gameState = data.state;
        this.myState = data.state === GameState.SETUP ? PlayerState.WORDS : PlayerState.WAIT;
        this.results = null;
    };

    @action.bound
    cmdPrepare (data: { players: { [player: string]: any[] }}) {
        this.players = {};
        for (const [name, v] of Object.entries(data.players)) {
            this.players[name] = {
                name: name,
                words: v[0],
                avatar: v[1] || `https://robohash.org/${name}?set=set4`
            };
        }
    };

    @action.bound
    cmdWait (data: any) {
        this.gameState = GameState.SETUP;
    };

    @action.bound
    cmdTour (data: any) {
        this.tourNumber = data.tour === undefined ? null : data.tour;
        this.gameState = GameState.PLAY;
        this.uistore.setTourDialogOpen(true);
    };

    @action.bound
    cmdTurn (data: any) {
        this.turnNumber = data.turn || null;
        this.explainer = data.explain || null;
        this.guesser = data.guess || null;
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
        this.turnWords = [];
    };

    @action.bound
    cmdStart (data: any) {
        if (this.myRole !== PlayerRole.WATCHER) {
            this.myState = PlayerState.PLAY;
            startBell.play();
        }
        this.timerStart = new Date();
        this.updateTimeLeft();
    };

    @action.bound
    cmdNext (data: any) {
        this.currentWord = data.word;
    };

    @action.bound
    cmdExplained (data: any) {
        this.turnWords.push(data.word);
    };

    @action.bound
    cmdMissed (data: any) {
        this.turnWords.push('--- не угадали ---');
    };

    @action.bound
    cmdStop (data: any) {
        if (data.reason === 'timer') {
            timeoutBell.play();
            this.myState = PlayerState.LAST_ANSWER;
        } else {
            // reason = empty
            this.myState = PlayerState.FINISH;
        }
    };

    @action.bound
    cmdFinish (data: any) {
        this.gameState = GameState.FINISH;
        this.timerStart = null;
        this.results = data.results || null;
    };

    @action.bound
    cmdError (data: any) {

    };
}