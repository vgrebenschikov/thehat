import React from "react";
import {Container, createStyles, Drawer, styled, Theme, Typography, withStyles} from "@material-ui/core";
import {inject, observer} from 'mobx-react';
import MobxReactRouter from "mobx-react-router";

import DataStore from "store/DataStore";
import Game from "store/Game";
import UIStore from "store/UIStore";
import {GameState, PlayerRole, PlayerState} from "store/types";

import StatusSurface from "common/StatusBar";
import UnstartedDrawer from "unstarted/UnstartedDrawer";
import WordsEntry from "unstarted/WordsEntry";
import InGameDrawer from "ingame/InGameDrawer";
import GuesserInterface from "ingame/GuesserInterface";
import {PleaseWait} from "ingame/PleaseWait";

const SideDrawer = inject('datastore')(observer((props: {datastore?: DataStore}) => {
    const isConfig = props.datastore?.game?.gameState === GameState.SETUP;
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

const StatusBar = inject('datastore')(observer((props: {datastore?: DataStore}) => {
    const {game} = props.datastore!;
    let status = `GS: ${game?.gameState}, PS: ${game?.myState}, PR: ${game?.myRole}`;
    return <StatusSurface>
        <Typography variant="h6">{status}</Typography>
    </StatusSurface>;
}));

const MainContainer = styled(Container)(({theme}) => ({
    flexGrow: 1,
    display: "flex",
    flexDirection: 'column',
})) as typeof Container;

const GameContent = observer((props: {game: Game}) => {
    const {game} = props;
    if (game.myState === PlayerState.WORDS) {
        return <WordsEntry/>;
    }
    if (game.myState === PlayerState.WAIT) {
        return <PleaseWait/>;
    }
    if (game.myRole !== PlayerRole.WATCHER) {
        return <GuesserInterface/>;
    }
    return null;
});

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
            <MainContainer>
                {datastore!.game && <GameContent game={datastore!.game}/>}
                <Drawer classes={{paper:classes.drawer}} anchor="left" open={uistore!.drawerOpen} onClose={()=>uistore!.setDrawerOpen(false)}>
                    <SideDrawer/>
                </Drawer>
            </MainContainer>
        </>;
    }
}

export default withStyles(styles)(MainApp);
