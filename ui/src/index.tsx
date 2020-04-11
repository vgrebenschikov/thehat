import React from 'react';
import ReactDOM from 'react-dom';
import './styles/reset.scss';
import './styles/index.scss';
import App from './App';
import * as serviceWorker from './serviceWorker';
import {RouterStore, syncHistoryWithStore} from "mobx-react-router";
import {createBrowserHistory} from "history";
import {Provider} from "mobx-react";
import {Router} from "react-router";

const browserHistory = createBrowserHistory({
  basename: '/',
});
const routingStore = new RouterStore();
const history = syncHistoryWithStore(browserHistory, routingStore);

ReactDOM.render(
  <React.StrictMode>
    <Provider routing={routingStore}>
      <Router history={history}>
        <App />
      </Router>
    </Provider>
  </React.StrictMode>,
  document.getElementById('root')
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
