import React from "react";
import {inject, observer} from "mobx-react";
import {Button, styled, Typography} from "@material-ui/core";
import DataStore from "store/DataStore";
import {Card} from "common/Card";
import Game from "../store/Game";
import {PlayerState} from "../store/types";
import TurnDescription from "./TurnDescription";
import {ReadyButton, Timer, WaitingCard} from "./CommonCards";

const WordShow = styled(Card)(({theme}) => ({
  marginTop: '48px',
  '& .centered': {
    margin: '0 auto',
    padding: '48px',
  },

})) as typeof Card;

const MainBody = observer((props: {game: Game}) => {
  const {game} = props;
  if (game.myState === PlayerState.BEGIN) {
    return <ReadyButton game={game}/>;
  }

  if (game.myState === PlayerState.READY) {
    return <WaitingCard/>;
  }

  if (game.myState === PlayerState.PLAY || game.myState === PlayerState.LAST_ANSWER) {
    return <>
      <WordShow>
        <Typography className="centered" variant="h2">
          {game.currentWord}
        </Typography>
      </WordShow>
      <Card>
        <Button className="full-width-button"
                variant="contained"
                color="primary"
                onClick={() => game.sendGuessed(true)}>
          Угадали
        </Button>
      </Card>
      <Card>
        <Button className="full-width-button"
                variant="contained"
                color="secondary"
                onClick={() => game.sendGuessed(false)}>
          Не угадали
        </Button>
      </Card>
      {game.myState === PlayerState.LAST_ANSWER &&
      <Card>
          <Typography variant="body1" className="centered" color="error">
              Последняя попытка...
          </Typography>
      </Card>
      }
    </>
  }
  return null;
});

export default inject('datastore')(observer((props: {datastore?: DataStore}) => {
  const {game} = props.datastore!;
  return <>
    <TurnDescription/>
    {game && <MainBody game={game}/>}
    {game?.myState === PlayerState.PLAY && <Timer/>}
  </>;
}));