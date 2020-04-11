import {inject, observer} from "mobx-react";
import DataStore from "../store/DataStore";
import React from "react";
import {
  createStyles,
  List,
  ListItem,
  ListItemSecondaryAction,
  ListItemText,
  Theme,
  Typography
} from "@material-ui/core";
import {makeStyles} from "@material-ui/core/styles";

const styles = (theme: Theme) => createStyles({
  numWords: {
    height: '40px',
    padding: '10px 24px',
    color: theme.palette.primary.contrastText,
    backgroundColor: theme.palette.primary.main,
    display: 'flex',
    alignItems: 'center',
  }
});
const useStyles = makeStyles(styles);

const PersonItem = (props: {person: string, ready: boolean}) => {
  return <ListItem>
    <ListItemText primary={props.person}/>
    {props.ready && <ListItemSecondaryAction><i className="material-icons-round">check</i></ListItemSecondaryAction>}
  </ListItem>
};

export default inject('datastore')(observer((props: {datastore?: DataStore}) => {
  const classes = useStyles();
  const game = props.datastore?.game!;
  const numWords = game.data?.words?.length || 0;
  return <>
    <div className={classes.numWords}>
      <Typography variant="h6">Слов в шляпе: {numWords}</Typography>
    </div>
    <List>
      {game.data?.users.map((user) => {
        return <PersonItem person={user.name} ready={!!game.data?.ready[user.uid]} key={user.uid}/>
      })}
    </List>
  </>;
}));
