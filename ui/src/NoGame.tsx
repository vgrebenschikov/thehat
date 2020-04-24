import {Button, Container, styled, Theme} from '@material-ui/core';
import {withStyles} from '@material-ui/core/styles';
import {inject, observer} from 'mobx-react';
import React from 'react';
import MobxReactRouter from "mobx-react-router";
import DataStore from "./store/DataStore";


const MidButton = styled(Button)({
    margin: '16px auto',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
}) as typeof Button;

const styles = (theme: Theme) => ({
    button: {
        margin: theme.spacing(2),
    },
});

interface NoGameProps {
    routing?: MobxReactRouter.RouterStore;
    datastore?: DataStore;
}

@inject('routing', 'datastore')
@observer
class NoGame extends React.Component<NoGameProps, any> {
    start_new_game = async () => {
        const id = await this.props.datastore!.createGame();
        this.props.routing!.push(`/${id}`);
    };

    render() {
        return <>
            <Container>
                <MidButton variant="contained" color="secondary" onClick={this.start_new_game}>Новая игра</MidButton>
            </Container>
        </>;
    }
}
export default withStyles(styles)(NoGame);
