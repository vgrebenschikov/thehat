const Chance = require("chance");

const consonants = 'бвгджзклмнпрстфхчш'.split('');
const vowels = 'аеиоу'.split('');


class RuLette {
    chance: any;

    constructor() {
        this.chance = new Chance();
    }

    slog() {
        return this.chance.pickone(consonants) + this.chance.pickone(vowels);
    }

    id() {
        const need_last_consonant = this.chance.bool();
        return this.slog() + 
                this.slog() + 
                this.slog() + 
                (need_last_consonant ? this.chance.pickone(consonants) : '');
    }
}

export default RuLette;