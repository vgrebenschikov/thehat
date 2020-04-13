import {inject, observer} from "mobx-react";
import DataStore from "../store/DataStore";
import React from "react";
import {Box, List, ListItem, ListItemSecondaryAction, ListItemText, styled, Typography} from "@material-ui/core";

const PersonItem = (props: {person: string, ready: boolean}) => {
  return <ListItem>
    <ListItemText primary={props.person}/>
    {props.ready && <ListItemSecondaryAction><i className="material-icons-round">check</i></ListItemSecondaryAction>}
  </ListItem>
};

const NumWords = styled(Box)(({theme}) => ({
  height: '40px',
  padding: '10px 24px',
  color: theme.palette.primary.contrastText,
  backgroundColor: theme.palette.primary.main,
  display: 'flex',
  alignItems: 'center',
}));


export default inject('datastore')(observer((props: {datastore?: DataStore}) => {
  const game = props.datastore?.game!;
  const numPlayers = game.players.length;
  return <>
    <NumWords>
      <Typography variant="h6">Игроков: {numPlayers}</Typography>
    </NumWords>
    <List>
      {game.players.map((user) => {
        return <PersonItem person={user.name} ready={false} key={user.uid}/>
      })}
    </List>
    {/*<PlayButton/>*/}
  </>;
}));
