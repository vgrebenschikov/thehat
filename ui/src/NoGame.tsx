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

const MidButton = styled(Button)({
    margin: '16px auto',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
}) as typeof Button;

class NewGameDialogStore extends DialogStore {
    @observable name: string = 'Интересная игра';
    @observable numwords: number = 5;
    @observable timer: number = 20;
}

interface NoGameProps {
    routing?: MobxReactRouter.RouterStore;
    datastore?: DataStore;
}

@inject('routing', 'datastore')
@observer
export default class NoGame extends React.Component<NoGameProps, any> {
    @observable ds: NewGameDialogStore;
    constructor(props: NoGameProps) {
        super(props);
        this.ds = new NewGameDialogStore(this.start_new_game);
    }

    start_new_game = async () => {
        const id = await this.props.datastore!.createGame(this.ds.name, this.ds.numwords, this.ds.timer);
        this.props.routing!.push(`/${id}`);
    };

    render() {
        return <>
            <Container>
                <MidButton variant="contained" color="secondary" onClick={this.ds.open}>Новая игра</MidButton>
            </Container>
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
