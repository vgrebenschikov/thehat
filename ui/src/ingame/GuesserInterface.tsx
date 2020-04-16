import React from "react";
import {inject, observer} from "mobx-react";
import {Button, Typography} from "@material-ui/core";

import DataStore from "store/DataStore";
import Game from "store/Game";
import {PlayerState} from "store/types";

import {MidCard} from "common/Card";
import Timer from "ingame/Timer";
import TurnDescription from "./TurnDescription";

const MainBody = observer((props: {game: Game}) => {
  const {game} = props;
  if (game.myState === PlayerState.BEGIN) {
    return <MidCard>
      <Button className="full-width-button"
              variant="contained"
              onClick={() => game.sendReady()}
              color="primary">
        Готов, начинаем!
      </Button>
    </MidCard>
  }

  if (game.myState === PlayerState.READY) {
    return <MidCard>
      <Typography variant="body1" className="centered">
        Ждем готовности оппонента...
      </Typography>
    </MidCard>
  }

  if (game.myState === PlayerState.PLAY) {
    return <>
      <MidCard>
        <Typography variant="h3" className="centered">
          Отгадывайте!
        </Typography>
      </MidCard>
      {game?.turnWords?.length>0 && <MidCard>
          <Typography variant="body2" className="centered">
              Последнее отгаданное слово: {game?.turnWords[-1]}
          </Typography>
      </MidCard>}
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
    {game?.myState == PlayerState.PLAY && <Timer/>}
  </>;
});