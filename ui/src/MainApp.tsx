import {Container, createStyles, Drawer, Paper, styled, Theme, Typography, withStyles} from "@material-ui/core";
import {inject, observer} from 'mobx-react';
import React from "react";
import DataStore from "store/DataStore";
import UIStore from "store/UIStore";
import UnstartedDrawer from "unstarted/UnstartedDrawer";
import InGameDrawer from "ingame/InGameDrawer";
import MobxReactRouter from "mobx-react-router";
import WordsEntry from "unstarted/WordsEntry";
import {GameState, PlayerState} from "./store/types";

const SideDrawer = inject('datastore')(observer((props: {datastore?: DataStore}) => {
    const isConfig = props.datastore?.game?.gameState === GameState.ST_CONFIG;
    return isConfig ? <UnstartedDrawer/> : <InGameDrawer/>;
}));

const styles = (theme: Theme) => createStyles({
    drawer: {
        width: '60vw',
        maxWidth: '350px',
        minWidth: '160px',
    },
    statusBar: {
        padding: '8px',
        marginBottom: '16px',
    },
});

const StatusSurface = styled(Paper)({
    padding: '8px',
    marginBottom: '16px',
});

const StatusBar = inject('datastore')(observer((props: {datastore?: DataStore}) => {
    let status = '';
    const {game} = props.datastore!;
    switch (game?.gameState) {
        case GameState.ST_CONFIG:
            status = `Добавить слова в шляпу (${game?.gameNumWords} шт)`;
            break;
        case GameState.ST_PLAY:
            status = `Играем!`;
            break;
        case GameState.ST_TURNSTART:
            status = `Приготовиться!`;
            break;
        case GameState.ST_TURN:
            status = `Отгадываем!`;
            break;
        case GameState.ST_AFTERTURN:
            status = `Время вышло`;
            break;
        case GameState.ST_FINISH:
            status = `Игра окончена`;
            break;

    }
    return <StatusSurface>
        <Typography variant="h6">{status}</Typography>
    </StatusSurface>;
}));

interface MainAppProps {
    datastore?: DataStore;
    uistore?: UIStore;
    routing?: MobxReactRouter.RouterStore;
    match: any;
    classes: any;
}

@inject('datastore','uistore','routing')
@observer
class MainApp extends React.Component<MainAppProps, {}> {
    constructor(props: MainAppProps) {
        super(props);
        props.datastore?.joinGame(props.match.params.gameId);
    }

    render() {
        const { datastore, uistore, classes } = this.props;
        return <>
            <StatusBar/>
            <Container>
                {datastore!.game?.myState === PlayerState.ST_WORDS && <WordsEntry/>}
                <Drawer classes={{paper:classes.drawer}} anchor="left" open={uistore!.drawerOpen} onClose={()=>uistore!.setDrawerOpen(false)}>
                    <SideDrawer/>
                </Drawer>
            </Container>
        </>;
    }
}

export default withStyles(styles)(MainApp);