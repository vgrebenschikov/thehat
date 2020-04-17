import React from 'react';
import DataStore from "../store/DataStore";
import {inject, observer} from "mobx-react";
import {Box, styled, Theme} from "@material-ui/core";

type TimerProps = {red: boolean};
const TimerSurface = styled(Box)<Theme, TimerProps>(({theme, red}) => ({
  margin: 'auto auto 16px auto',
  fontSize: '96px',
  color: (red ? theme.palette.error.main : theme.palette.text.primary),
}));

export default inject('datastore')(observer((props: {datastore?: DataStore}) => {
  const {game} = props.datastore!;
  let show = 0;
  if (!game || game!.timeLeft === null) {
    // return null;

  } else {show = 22;}
  // return <TimerSurface red={game.timeLeft < 5}>{game.timeLeft}</TimerSurface>;
  return <TimerSurface red={true}>{show}</TimerSurface>;
}));