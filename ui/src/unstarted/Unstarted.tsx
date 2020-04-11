import {inject, observer} from "mobx-react";
import React from "react";
import {Button, createStyles, IconButton, Paper, Theme, WithStyles, withStyles} from "@material-ui/core";
import DataStore from "store/DataStore";

const styles = (theme: Theme) => createStyles({
  button: {
    margin: theme.spacing(2),
  },
  bottom: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    boxShadow: '0 0 4px black',
    borderRadius: 0,
    height: '48px',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  },
  readyButton: {
    width: '100%',
    height: '100%',
  },
  card: {
    padding: '16px',
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'stretch',
    marginBottom: '8px',
  },
  cardContent: {
    fontsize: '24px',
    color: theme.palette.text.primary,
    flexGrow: 1,
  },
  cardIcon: {
    flexGrow: 0,
  }
});

interface CardProps extends WithStyles<typeof styles> {}

@observer
class _WordCard extends React.Component<CardProps, any> {
  render() {
    const {classes} = this.props;
    return <Paper className={classes.card}>
      <div className={classes.cardContent}>карова</div>
      <IconButton className={classes.cardIcon}><i className="material-icons-round">delete</i></IconButton>
    </Paper>;
  }
}
const WordCard = withStyles(styles)(_WordCard);

@observer
class _AddButton extends React.Component<CardProps, any> {
  render() {
    const {classes} = this.props;
    return <Paper className={classes.card}>
      <Button className={classes.cardContent}><i className="material-icons-round">add</i></Button>
    </Paper>;
  }
}
const AddButton = withStyles(styles)(_AddButton);


interface UnstartedProps {
  datastore?: DataStore;
  classes: any;
}

@inject('datastore')
@observer
class Unstarted extends React.Component<UnstartedProps, {}> {
  render() {
    const {classes} = this.props;
    return <>
      <WordCard></WordCard>
      <AddButton/>
      <Paper className={classes.bottom}>
        <Button className={classes.readyButton}><i className="material-icons-round">check</i>Готово</Button>
      </Paper>
    </>;
  }
}

export default withStyles(styles)(Unstarted);
