import React from "react";
import { Button, Container, Paper, styled, Typography } from "@material-ui/core";
import { inject, observer } from 'mobx-react';

import DataStore from "store/DataStore";
import Game from "store/Game";
import { GameState, PlayerRole, PlayerState } from "store/types";

import WordsEntry from "unstarted/WordsEntry";
import WaitingForStartInterface from "unstarted/WaitingForStartInterface";
import GuesserInterface from "ingame/GuesserInterface";
import { MidCard } from "common/Card";
import ExplainerInterface from "ingame/ExplainerInterface";
import tourDescripton from "tourDescription";
import TurnChangeDialog from "TurnChangeDialog";
import { ConnectionStatus } from "store/WebSocketConnection";
import Results from "Results";
import WaitingPlayerInterface from "ingame/WaitingPlayerInterface";
import Drawer from 'drawer/Drawer';

const StatusSurface = styled(Paper)({
    padding: '8px',
    marginBottom: '16px',
}) as typeof Paper;

const StatusBar = inject('datastore')(observer((props: { datastore?: DataStore }) => {
    const { game } = props.datastore!;
    let status = '';
    if (game?.myState === PlayerState.WORDS) {
        status = `Придумывайте слова (${game?.gameNumWords} штук)`;
    } else if (game?.tourNumber || game?.tourNumber === 0) {
        status = tourDescripton[game?.tourNumber];
    }
    return <StatusSurface>
        <Typography variant="h6">{status}</Typography>
    </StatusSurface>;
}));

const MainContainer = styled(Container)(({ theme }) => ({
    flexGrow: 1,
    display: "flex",
    flexDirection: 'column',
    minHeight: 0,
})) as typeof Container;

const GameContent = observer((props: { game: Game }) => {
    const { game } = props;
    if (game.myState === PlayerState.WORDS) {
        return <WordsEntry />;
    }
    if (game.gameState === GameState.FINISH && game.results) {
        return <Results />;
    }

    if (game.myState === PlayerState.WAITSTART) {
        return <WaitingForStartInterface />;
    }
    if (game.myState === PlayerState.WAIT) {
        return <WaitingPlayerInterface />;
    }
    if (game.myRole === PlayerRole.GUESSER) {
        return <GuesserInterface />;
    }
    if (game.myRole === PlayerRole.EXPLAINER) {
        return <ExplainerInterface />;
    }

    return null;
});

@inject('datastore')
@observer
class BadWebsocket extends React.Component<{ datastore?: DataStore }, any> {
    render_reconnecting() {
        return <Typography className="centered" variant="body1">Нет связи, пытаемся пробиться...</Typography>;
    }
    render_disconnected() {
        const { ws } = this.props.datastore!.game!;
        return <>
            <Typography className="content" variant="body1">Всё пропало! Попробуем ещё?</Typography><br />
            <Button className="content" variant="contained" onClick={() => ws.reconnectManually()}>ОК</Button>
        </>;
    }
    render() {
        const { ws } = this.props.datastore!.game!;
        return <MidCard>
            {ws.connectionStatus === ConnectionStatus.Disconnected ?
                this.render_disconnected() :
                this.render_reconnecting()
            }
        </MidCard>;
    }
}

interface MainAppProps {
    datastore?: DataStore;
    match: any;
}

@inject('datastore')
@observer
export default class MainApp extends React.Component<MainAppProps, {}> {
    constructor(props: MainAppProps) {
        super(props);
        props.datastore?.joinGame(props.match.params.gameId);
    }

    render() {
        const { game } = this.props.datastore!;
        if (game?.ws.connectionStatus === ConnectionStatus.Disconnected
            || game?.ws.connectionStatus === ConnectionStatus.Retrying) {
            return <MainContainer>
                <BadWebsocket />
            </MainContainer>;
        }
        return <>
            <StatusBar />
            <MainContainer>
                {game && <GameContent game={game} />}
            </MainContainer>
            <TurnChangeDialog />
            <Drawer />
        </>;
    }
}
