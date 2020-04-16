import {observer, Provider} from "mobx-react";
import React from 'react';
import DataStore from "store/DataStore";
import UIStore from "store/UIStore";
import MainApp from "./MainApp";
import NoGame from './NoGame';
import TopBar from "./TopBar";
import {Route, Switch} from "react-router";
import {Box, styled} from "@material-ui/core";

let store = new DataStore();
let uistore = new UIStore();

const FullScreen = styled(Box)(({theme}) => ({
  height: '100vh',
  width: '100vw',
  display: 'flex',
  flexDirection: 'column',
}));

function App() {
  return (
    <Provider datastore={store} uistore={uistore}>
      <FullScreen>
        <TopBar/>
        {store.user &&
        <Switch>
            <Route path="/:gameId" component={MainApp}/>
            <Route path="" component={NoGame}/>
        </Switch>
        }
      </FullScreen>
    </Provider>
  );
}

export default observer(App);
