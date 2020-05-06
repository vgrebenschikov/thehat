import React from "react";
import {Typography} from "@material-ui/core";
import {Card, MidCard} from "common/Card";
import {inject, observer} from "mobx-react";
import DataStore from "../store/DataStore";
import TurnDescription from "./TurnDescription";

@inject('datastore')
@observer
export default class WaitingPlayerInterface extends React.Component<{datastore?: DataStore}, {}> {
  render() {
    const {game} = this.props.datastore!;
    if (!game) {
      return <MidCard><Typography variant="h2">Ожидайте хода</Typography></MidCard>;
    }

    return <>
      <TurnDescription/>
      {(game?.turnWords || []).map((w: string, i: number) => <Card key={i}>
        <Typography variant="body2" className="centered">{w}</Typography>
      </Card>)}
    </>
  }
}