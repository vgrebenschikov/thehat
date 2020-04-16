import {inject, observer} from "mobx-react";
import DataStore from "../store/DataStore";
import React from "react";
import {
  Box,
  Button,
  List,
  ListItem,
  ListItemSecondaryAction,
  ListItemText,
  styled,
  Typography
} from "@material-ui/core";

const PersonItem = (props: {person: string, ready: boolean}) => {
  return <ListItem>
    <ListItemText primary={props.person}/>
    {props.ready && <ListItemSecondaryAction><i className="material-icons-round">check</i></ListItemSecondaryAction>}
  </ListItem>
};

const Title = styled(Box)(({theme}) => ({
  height: '40px',
  padding: '10px 24px',
  color: theme.palette.primary.contrastText,
  backgroundColor: theme.palette.primary.main,
  display: 'flex',
  alignItems: 'center',
}));

const BottomPad = styled(Box)(({theme}) => ({
  height: '40px',
  padding: '10px 24px',
  backgroundColor: theme.palette.background.paper,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  boxShadow: '0 0 4px',
}));

export default inject('datastore')(observer((props: {datastore?: DataStore}) => {
  const game = props.datastore?.game!;
  const numPlayers = game.players.length;
  return <>
    <Title>
      <Typography variant="h6">Игроков: {numPlayers}</Typography>
    </Title>
    <List>
      {game.players.map((user) => {
        return <PersonItem person={user.name} ready={user.done} key={user.uid}/>
      })}
    </List>
    <BottomPad>
      <Button variant="contained" color="primary" onClick={game.sendPlay}>Начать игру</Button>
    </BottomPad>
  </>;
}));
