import {
    Button,
    Container,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Grid,
    Input,
    Theme
} from '@material-ui/core';
import {withStyles} from '@material-ui/core/styles';
import {inject, observer} from 'mobx-react';
import React from 'react';
import MobxReactRouter from "mobx-react-router";
import RuLette from "./rulette";
import {action, observable} from "mobx";

const styles = (theme: Theme) => ({
    button: {
        margin: theme.spacing(2),
    },
});

class DialogStore {
    @observable isOpen: boolean = false;
    callback: () => void;

    constructor(callback: () => void) {
        this.callback = callback;
    }

    @action.bound
    open() {
        this.isOpen = true;
    }

    @action.bound
    close() {
        this.isOpen = false;
    }

    @action.bound
    submit() {
        this.isOpen = false;
        this.callback();
    }
}

class gameNameStore extends DialogStore {
    @observable name: string = '';
    constructor(callback: () => void) {
        super(callback);
    }

    @action.bound
    setName (name: string) {
        this.name = name;
    }
}

interface NoGameProps {
    routing?: MobxReactRouter.RouterStore;
    classes: any;
}

@inject("routing")
@observer
class NoGame extends React.Component<NoGameProps, any> {
    dialogStore: gameNameStore;

    constructor(props: NoGameProps) {
        super(props);
        this.dialogStore = new gameNameStore(this.do_join_game);
        this.state = {
            dialogOpen: false,
            gameName: ''
        };
    }

    do_join_game = () => {
        this.props.routing!.push(`/${this.dialogStore.name}`);
    };

    start_new_game = () => {
        const r = new RuLette();
        this.props.routing!.push(`/${r.id()}`);
    };

    render() {
        const { classes } = this.props;
        return <>
            <Container>
                <Grid container justify="center" spacing={2}>
                    <Grid item>
                        <Button
                            variant="contained"
                            className={classes!.button}
                            onClick={this.dialogStore.open}>
                            Join a game
                        </Button>
                        <Button
                            variant="contained"
                            color="secondary"
                            className={classes!.button}
                            onClick={this.start_new_game}>
                            Create game
                        </Button>
                    </Grid>
                    <Dialog open={this.dialogStore.isOpen}>
                        <DialogTitle>
                            Enter the game's name
                        </DialogTitle>
                        <form onSubmit={this.dialogStore.submit}>
                            <DialogContent>
                                <Input type="text"
                                       onChange={(ev) => this.dialogStore.setName(ev.target.value)}
                                       onSubmit={this.dialogStore.submit}
                                       autoFocus />
                            </DialogContent>
                            <DialogActions>
                                <Button onClick={this.dialogStore.close}>Cancel</Button>
                                <Button type="submit" variant="contained" color="primary" onClick={this.dialogStore.submit}>Join</Button>
                            </DialogActions>
                        </form>
                    </Dialog>
                </Grid>
            </Container>
        </>;
    }
}
export default withStyles(styles)(NoGame);
