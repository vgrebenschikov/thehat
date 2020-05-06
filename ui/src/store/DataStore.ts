import { action, computed, observable } from "mobx";
import UIStore from "store/UIStore";
import Game, { User } from "./Game";

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
    }

    @action
    signIn = (response: any) => {
        console.log('resp=', response);
        if (response.profileObj) {
            this.user = response.profileObj;
        } else if (response.error) {
            this.loginError = response.error;
        }
    };

    createGame = async (name: string, numwords: number, timer: number) => {
        const url = process.env.NODE_ENV === 'development'
          ? `//${window.location.hostname}:8088/games`
          : `//${window.location.host}/games`;

        const resp = await fetch(url, {
            method: 'POST',
            cache: 'no-cache',
            redirect: 'follow',
            referrerPolicy: 'no-referrer',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({name, numwords, timer}),
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
