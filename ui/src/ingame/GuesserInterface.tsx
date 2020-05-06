import React from "react";
import {inject, observer} from "mobx-react";
import {Typography} from "@material-ui/core";

import DataStore from "store/DataStore";
import Game from "store/Game";
import {PlayerState} from "store/types";

import {Card, MidCard} from "common/Card";
import TurnDescription from "./TurnDescription";
import {ReadyButton, Timer, WaitingCard} from "./CommonCards";

const MainBody = observer((props: {game: Game}) => {
  const {game} = props;
  if (game.myState === PlayerState.BEGIN) {
    return <ReadyButton game={game}/>;
  }

  if (game.myState === PlayerState.READY) {
    return <WaitingCard/>;
  }

  if (game.myState === PlayerState.PLAY) {
    return <>
      {(game?.turnWords || []).map((w: string, i: number) => <Card key={i}>
        <Typography variant="body2" className="centered">{w}</Typography>
      </Card>)}
      <MidCard>
        <Typography variant="h3" className="centered">
          Отгадывайте!
        </Typography>
      </MidCard>
    </>
  }
  if (game?.myState === PlayerState.LAST_ANSWER) {
    return <MidCard>
      <Typography variant="body1" className="centered" color="error">
        Последняя попытка...
      </Typography>
    </MidCard>;
  }
  return null;
});

export default inject('datastore')((props: {datastore?: DataStore}) => {
  const {game} = props.datastore!;
  return <>
    <TurnDescription/>
    {game && <MainBody game={game}/>}
    {game?.myState === PlayerState.PLAY && <Timer/>}
  </>;
});