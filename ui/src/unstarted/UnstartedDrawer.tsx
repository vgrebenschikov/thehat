import {inject, observer} from "mobx-react";
import DataStore from "../store/DataStore";
import React from "react";
import {
  Avatar,
  Box,
  Button,
  List,
  ListItem, ListItemAvatar,
  ListItemSecondaryAction,
  ListItemText,
  styled,
  Typography
} from "@material-ui/core";
import {Player} from "../store/Game";

const DrawerContents = styled(Box)({
  width: '60vw',
  maxWidth: '400px',
  minWidth: '230px',
});

const PersonItem = (props: {user: Player}) => {
  const {name, words, avatar} = props.user;
  return <ListItem>
    <ListItemAvatar>
      <Avatar src={avatar}>??</Avatar>
    </ListItemAvatar>
    <ListItemText primary={name}/>
    {words > 0 && <ListItemSecondaryAction>{words}</ListItemSecondaryAction>}
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
  const numPlayers = game.playerList.length;
  return <DrawerContents>
    <Title>
      <Typography variant="h6">Игроков: {numPlayers}</Typography>
    </Title>
    <List>
      {game.playerList.map((user) => {
        return <PersonItem user={user} key={user.name}/>
      })}
    </List>
    <BottomPad>
      <Button variant="contained" color="primary" onClick={game.sendPlay}>Начать игру</Button>
    </BottomPad>
  </DrawerContents>;
}));
