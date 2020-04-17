import React from "react";
import {inject, observer} from "mobx-react";
import {Box, Button, styled, Theme, Typography} from "@material-ui/core";

import {MidCard} from "common/Card";
import Game from "store/Game";
import DataStore from "../store/DataStore";

export const ReadyButton = observer((props: {game: Game}) => {
  return <MidCard>
    <Button className="full-width-button"
            variant="contained"
            onClick={() => props.game.sendReady()}
            color="primary">
      Готов, начинаем!
    </Button>
  </MidCard>
});

export const WaitingCard = () => {
  return <MidCard>
    <Typography variant="body1" className="centered">
      Ждем готовности оппонента...
    </Typography>
  </MidCard>;
};

type TimerProps = { red: boolean };
export const TimerSurface = styled(Box)<Theme, TimerProps>(({theme, red}) => ({
  margin: 'auto auto 16px auto',
  fontSize: '96px',
  color: (red ? theme.palette.error.main : theme.palette.text.primary),
}));

export const Timer = inject('datastore')(observer((props: {datastore?: DataStore}) => {
  const {game} = props.datastore!;
  if (!game || game!.timeLeft === null) {
     return null;
  }
  return <TimerSurface red={game.timeLeft < 5}>{game.timeLeft}</TimerSurface>;
}));