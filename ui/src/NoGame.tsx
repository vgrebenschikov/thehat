import {
    Button,
    Container,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    styled,
    TextField
} from '@material-ui/core';
import {inject, observer} from 'mobx-react';
import React from 'react';
import MobxReactRouter from "mobx-react-router";
import DataStore from "./store/DataStore";
import {DialogStore} from "./common/DialogStore";
import {observable} from "mobx";
import { Typography } from '@material-ui/core';

const MidButton = styled(Button)({
    margin: '16px auto',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
}) as typeof Button;

class NewGameDialogStore extends DialogStore {
    @observable name: string = '';
    @observable numwords: number = 5;
    @observable timer: number = 20;
}

class JoinGameDialogStore extends DialogStore {
    @observable name: string = '';
}

interface NoGameProps {
    routing?: MobxReactRouter.RouterStore;
    datastore?: DataStore;
}

// 09b64c11-ac0e-4e60-843a-a17dd8d1a1b6
const game_id_re = RegExp('[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}');

@inject('routing', 'datastore')
@observer
export default class NoGame extends React.Component<NoGameProps, any> {
    @observable ds: NewGameDialogStore;
    @observable joinds: JoinGameDialogStore;
    @observable errmsg: string = '';

    constructor(props: NoGameProps) {
        super(props);
        this.ds = new NewGameDialogStore(this.start_new_game);
        this.joinds = new JoinGameDialogStore(this.join_game)
    }

    start_new_game = async () => {
        const id = await this.props.datastore!.createGame(this.ds.name, this.ds.numwords, this.ds.timer);
        this.props.routing!.push(`/${id}`);
    };

    open_join_dialog = () => {
        this.joinds.name = '';
        this.errmsg = '';
        this.joinds.open();
    };

    join_game = async () => {
        const found: number = this.joinds.name.search(game_id_re);
        let id: string = '';
        if (found === -1) {
            id = await this.props.datastore!.searchGame(this.joinds.name);
        } else {
            id = this.joinds.name.slice(found, found + 36);
        }
        if (id) {
            this.props.routing!.push(`/${id}`);
        } else {
            this.errmsg = `... Ой, что-то не нашлась игра "${this.joinds.name}" ...`;
            this.joinds.open();
        }
    };

    render() {
        return <>
            <Container>
                <MidButton variant="contained" color="secondary" onClick={this.open_join_dialog}>Присоединиться к игре</MidButton>
                <MidButton variant="contained" color="secondary" onClick={this.ds.open}>Новая игра</MidButton>
            </Container>
            <Dialog open={this.joinds.isOpen} onClose={this.joinds.close}>
                <form>
                    <DialogTitle>Присоединиться к игре</DialogTitle>
                    <DialogContent>
                        <TextField id="name" label="Имя" value={this.joinds.name} onChange={this.joinds.change('name')} fullWidth/>
                        (можно вводить имя игры, ссылку на игру или её номер)
                        {this.errmsg && <Typography variant="body2" color="error">{this.errmsg}</Typography>}
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={this.joinds.close}>Отмена</Button>
                        <Button onClick={this.joinds.submit} variant="contained" color="primary">Поехали!</Button>
                    </DialogActions>
                </form>
            </Dialog>
            <Dialog open={this.ds.isOpen} onClose={this.ds.close}>
                <form>
                    <DialogTitle>Начнём новую игру!</DialogTitle>
                    <DialogContent>
                        <TextField id="name" label="Имя игры" value={this.ds.name} onChange={this.ds.change('name')} fullWidth/>
                        <TextField id="numwords" label="Сколько слов придумываем" type="number" value={this.ds.numwords} onChange={this.ds.changenum('numwords')} fullWidth/>
                        <TextField id="timer" label="Секунд на ход" type="number" value={this.ds.timer} onChange={this.ds.changenum('timer')} fullWidth/>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={this.ds.close}>Отмена</Button>
                        <Button onClick={this.ds.submit} variant="contained" color="primary">Начали!</Button>
                    </DialogActions>
                </form>
            </Dialog>
        </>;
    }
}
