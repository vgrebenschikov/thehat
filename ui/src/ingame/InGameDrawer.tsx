import {inject, observer} from "mobx-react";
import DataStore from "../store/DataStore";
import React from "react";

export default inject('datastore')(observer((props: {datastore?: DataStore}) => {
  return <div>in-game drawer</div>;
}));
