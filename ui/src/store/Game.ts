import * as firebase from "firebase/app";
import "firebase/firestore";
import { observable, action } from 'mobx';
import { User } from 'firebase';
import { runInAction } from 'mobx';

export interface Player {
    name: string;
    uid: string;
}

export interface DBData {
    users: Player[];
    ready: { [uid: string]: boolean };
    started: boolean | undefined;

    words: string[];
}

export default class Game {
    @observable name: string;
    @observable data: DBData | null = null;

    db: firebase.firestore.Firestore;
    doc: firebase.firestore.DocumentReference | null = null;
    unsubscribe: (() => void) | null = null;
    user: Player | null = null;

    constructor(name: string, user: User) {
        this.db = firebase.firestore();
        this.name = name;
        this.loadGame(this.name, user);
    }

    loadGame = (name: string, user: User) => {
        name = name.toLowerCase();
        this.doc = this.db.collection('docs').doc(name);
        this.unsubscribe = this.doc.onSnapshot(action((doc: any) => {
            this.data = doc.data();
            this.name = name;
            console.log('got update:', doc.data())
        }));
        this.user = { name: user.displayName || '', uid: user.uid };
        this.doc.set({
            users: firebase.firestore.FieldValue.arrayUnion(this.user),
            ready: { [this.user.uid]: false }
        }, { merge: true });
    };

    leaveGame = async () => {
        await this.doc?.update({
            users: firebase.firestore.FieldValue.arrayRemove(this.user)
        });
        this.unsubscribe?.();
        runInAction(() => {
            this.data = null;
            this.name = '';
        });
    };

    addWord = async (word: string) => {
        await this.doc?.update({
            words: firebase.firestore.FieldValue.arrayUnion(word.toLowerCase())
        });
    };

    removeWord = async (word: string) => {
        await this.doc?.update({
            words: firebase.firestore.FieldValue.arrayRemove(word.toLowerCase())
        });
    };

    isStarted = (): boolean => {
        return !!(this.data?.started);
    }

}