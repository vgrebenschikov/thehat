import {Container, createStyles, Drawer, Paper, Theme, Typography, withStyles} from "@material-ui/core";
import {inject, observer} from 'mobx-react';
import React from "react";
import DataStore from "store/DataStore";
import UIStore from "store/UIStore";
import UnstartedDrawer from "unstarted/UnstartedDrawer";
import InGameDrawer from "ingame/InGameDrawer";
import MobxReactRouter from "mobx-react-router";
import Unstarted from "./unstarted/Unstarted";

const SideDrawer = inject('datastore')(observer((props: {datastore?: DataStore}) => {
    const isStarted = props.datastore?.game?.isStarted();
    return isStarted ? <InGameDrawer/> : <UnstartedDrawer/>;
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

interface MainAppProps {
    datastore?: DataStore;
    uistore?: UIStore;
    routing?: MobxReactRouter.RouterStore;
    match: any;
    classes: any;
}

const StatusBar = withStyles(styles)(inject('datastore')(observer((props: {datastore?: DataStore, classes: any}) => {
    return <Paper className={props.classes.statusBar}>
        <Typography variant="h6">
            {props.datastore?.game?.isStarted()
              ? "Играем!"
              : "Добавить слова в шляпу"}
        </Typography>
    </Paper>;
})));

@inject('datastore','uistore','routing')
@observer
class MainApp extends React.Component<MainAppProps, {}> {
    constructor(props: MainAppProps) {
        super(props);
        props.datastore?.joinGame(props.match.params.gameId);
    }

    leaveGame = async () => {
        await this.props.datastore?.leaveGame();
        this.props.routing!.push('/');
    };

    render() {
        const { datastore, uistore, classes } = this.props;
        if (!datastore!.game?.data) {
            return null;
        }
        return <>
            <StatusBar/>
            <Container>
                {datastore!.game?.isStarted() ? null : <Unstarted/>}
                <Drawer classes={{paper:classes.drawer}} anchor="left" open={uistore!.drawerOpen} onClose={()=>uistore!.setDrawerOpen(false)}>
                    <SideDrawer/>
                </Drawer>
            </Container>
        </>;
    }
}

export default withStyles(styles)(MainApp);