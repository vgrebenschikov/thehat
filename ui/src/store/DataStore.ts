import {User} from "firebase";
import * as firebase from "firebase/app";
import "firebase/auth";
import "firebase/firestore";
import {action, computed, observable, runInAction} from "mobx";
import Game from "./Game";
import firebaseConfig from 'firebase-config';
import UIStore from "store/UIStore";

export default class DataStore {
    @observable user: User | null = null;
    @observable userName: string = '';
    @observable loginError: string | null = null;

    @observable game: Game | null = null;

    @observable ownWords: string[] = [];

    private uistore: UIStore;

    @computed
    get currentGame() {
        if (this.game === null) {
            return null;
        }
        return this.game.id;
    };

    constructor(uistore: UIStore) {
        this.uistore = uistore;
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

    createGame = async () => {
        const url = process.env.NODE_ENV === 'development'
          ? `//${window.location.hostname}:8088/games`
          : `//${window.location.host}/games`;

        const data = {
            name: 'Secret Tea',
            numwords: 6,
            timer: 20,
        };
        const resp = await fetch(url, {
            method: 'POST',
            cache: 'no-cache',
            redirect: 'follow',
            referrerPolicy: 'no-referrer',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
          });
        const ret = await resp.json();
        return ret.id;
    };

    joinGame = action((name: string) => {
        if (this.game?.id !== name) {
            this.game = new Game(name, this.user!, this.uistore);
        }
    });

    get inGame(): boolean {
        return !!this.game;
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
