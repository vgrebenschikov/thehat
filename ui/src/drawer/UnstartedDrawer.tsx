import React from "react";
import { inject, observer } from "mobx-react";
import {
  Avatar,
  Button,
  List,
  ListItem, ListItemAvatar,
  ListItemSecondaryAction,
  ListItemText,
  Typography
} from "@material-ui/core";

import DataStore from "store/DataStore";
import { Player } from "store/Game";

import { DrawerContents, Title, BottomPad } from 'drawer/DrawerCards';


const PersonItem = (props: { user: Player }) => {
  const { name, words, avatar } = props.user;
  return <ListItem>
    <ListItemAvatar>
      <Avatar src={avatar}>??</Avatar>
    </ListItemAvatar>
    <ListItemText primary={name} />
    {words > 0 && <ListItemSecondaryAction>{words}</ListItemSecondaryAction>}
  </ListItem>
};


export default inject('datastore')(observer((props: { datastore?: DataStore }) => {
  const game = props.datastore?.game!;
  const numPlayers = game.playerList.length;
  return <DrawerContents>
    <Title>
      <Typography variant="h6">Игроков: {numPlayers}</Typography>
    </Title>
    <List>
      {game.playerList.map((user) => {
        return <PersonItem user={user} key={user.name} />
      })}
    </List>
    <BottomPad>
      <Button variant="contained" color="primary" onClick={game.sendPlay}>Начать игру</Button>
    </BottomPad>
  </DrawerContents>;
}));
