import {User} from "firebase";
import * as firebase from "firebase/app";
import "firebase/auth";
import "firebase/firestore";
import {action, computed, observable, runInAction} from "mobx";
import Game from "./Game";
import firebaseConfig from 'firebase-config';
import WebSocketConnection from "./WebSocketConnection";

export default class DataStore {
    @observable user: User | null = null;
    @observable userName: string = '';
    @observable loginError: string | null = null;

    @observable game: Game | null = null;

    @observable ownWords: string[] = [];

    @observable websocket: WebSocketConnection = new WebSocketConnection();

    @computed
    get currentGame() {
        if (this.game === null) {
            return null;
        }
        return this.game.id;
    };

    constructor() {
        this.websocket.establishConnection();
        this.websocket.subscribeReceiver(this.onWebsocketMessage);
        firebase.initializeApp(firebaseConfig);
        firebase.auth().onAuthStateChanged(action((user: User | null) => {
            this.user = user;
        }));
    }

    signIn = async () => {
        try {
            await firebase.auth().signInWithPopup(new firebase.auth.GoogleAuthProvider())
        } catch (reason) {
            runInAction(() => { this.loginError = reason.code })
        }
    };

    joinGame = action((name: string) => {
        if (this.game?.id !== name) {
            this.game = new Game(name, this.user!, this.websocket);
        }
    });

    get inGame(): boolean {
        return !!this.game;
    }

    setUserName = action((name: string) => {
        if (!this.user?.isAnonymous) {
            return;
        }
        this.user.updateProfile({ displayName: name })
            .then(action(() => {
                this.userName = this.user?.displayName || '';
            }));
    });

    onWebsocketMessage(data: any) {
        console.log('received websocket data: ', data);
    }

    @action
    deleteOwnWord(w: string) {
        this.ownWords = this.ownWords.filter((ow) => (ow !== w));
    }

    @action
    addOwnWord(w: string) {
        this.ownWords.indexOf(w) === -1 && this.ownWords.push(w);
    }

    @action
    async sendWords() {
        this.game?.sendWords(this.ownWords);
        this.ownWords = [];
    }
}
