import React from "react";
import {Avatar, Box, styled, Typography} from "@material-ui/core";
import {inject, observer} from "mobx-react";

import DataStore from "store/DataStore";
import {PlayerRole} from "store/types";

import {Card} from "common/Card";
import Game from "../store/Game";

const You = styled(Box)(({theme}) => ({
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
  padding: '8px',
  margin: '0 8px',
  borderRadius: '4px',
  display: 'inline',
}));

const Layout = styled(Box)({
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  padding: '8px',
  margin: '0 auto',
  '& .left': {
    flexGrow: 1,
    marginRight: '8px',
    marginLeft: 'auto',
  },
  '& .right': {
    flexGrow: 1,
    marginLeft: '8px',
  }
});

const PlayerDisplay = styled(Box)({
  display: 'flex',
  alignItems: 'center',
}) as typeof Box;

const PlayerAvatar = observer((props: { game: Game, player: string|null }) => {
  if (!props.player) {
    return null;
  }
  const { game: {players} } = props;
  const url = players[props.player].avatar;
  return <Avatar src={url}/>;
});

export default inject('datastore')(observer((props: {datastore?: DataStore }) => {
  const { game } = props.datastore!;
  const explainer = game?.myRole === PlayerRole.EXPLAINER ? <You>Вы</You> : game?.explainer;
  const guesser = game?.myRole === PlayerRole.GUESSER ? <You>Вы</You> : game?.guesser;
  return <Card>
    <Layout>
      <PlayerDisplay className="left">
        <Typography variant="h6">{explainer}</Typography>
        <PlayerAvatar game={game!} player={game!.explainer}/>
      </PlayerDisplay>
      <Typography variant="h6">&nbsp;&nbsp;&nbsp; >>> &nbsp;&nbsp;&nbsp;</Typography>
      <PlayerDisplay className="right">
        <PlayerAvatar game={game!} player={game!.guesser}/>
        <Typography variant="h6">{guesser}</Typography>
      </PlayerDisplay>
    </Layout>
  </Card>
}));
