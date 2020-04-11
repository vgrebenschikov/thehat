import {observer, Provider} from "mobx-react";
import React from 'react';
import DataStore from "store/DataStore";
import UIStore from "store/UIStore";
import MainApp from "./MainApp";
import NoGame from './NoGame';
import TopBar from "./TopBar";
import {Route, Switch} from "react-router";

let store = new DataStore();
let uistore = new UIStore();

function App() {
  return (
    <Provider datastore={store} uistore={uistore}>
      <TopBar/>
      {store.user &&
      <Switch>
          <Route path="/:gameId" component={MainApp}/>
          <Route path="" component={NoGame}/>
      </Switch>
      }
    </Provider>
  );
}

export default observer(App);
