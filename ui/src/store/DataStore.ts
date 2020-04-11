import {User} from "firebase";
import * as firebase from "firebase/app";
import "firebase/auth";
import "firebase/firestore";
import {action, computed, observable, runInAction} from "mobx";
import Game from "./Game";
import RuLette from '../rulette';

export default class DataStore {
    @observable user: User | null = null;
    @observable userName: string = '';
    @observable loginError: string | null = null;

    @observable game: Game | null = null;

    @observable ownWords: string[] = [];

    @computed
    get currentGame() {
        if (this.game === null) {
            return null;
        }
        return this.game.name;
    };

    constructor() {
        const firebaseConfig = {
            apiKey: "AIzaSyB6NeHhDMD0xFmncv6gdm0QfXWslGkIX7o",
            authDomain: "cotif-272120.firebaseapp.com",
            databaseURL: "https://cotif-272120.firebaseio.com",
            projectId: "cotif-272120",
            storageBucket: "cotif-272120.appspot.com",
            messagingSenderId: "805848413148",
            appId: "1:805848413148:web:e3e8606c8aaa2fee1b9519",
            measurementId: "G-CFFSQHQZXL"
        };
        firebase.initializeApp(firebaseConfig);
        firebase.auth().onAuthStateChanged(this.authChanged);
    }

    authChanged = action((user: User | null) => {
        // if (!user?.isAnonymous) {
        this.user = user;
        // }
    });

    signIn = async () => {
        try {
            await firebase.auth().signInWithPopup(new firebase.auth.GoogleAuthProvider())
        } catch (reason) {
            runInAction(() => { this.loginError = reason.code })
        }
    };

    leaveGame = async () => {
        await this.game?.leaveGame();
        runInAction(() => {
            this.game = null;
        });
    };

    joinGame = action((name: string) => {
        this.game = new Game(name, this.user!);
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
}
