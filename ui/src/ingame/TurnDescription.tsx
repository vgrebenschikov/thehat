import React from "react";
import {Box, styled, Typography} from "@material-ui/core";
import {inject} from "mobx-react";

import DataStore from "store/DataStore";
import {PlayerRole} from "store/types";

import {Card} from "common/Card";

const You = styled(Box)(({theme}) => ({
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
  padding: '8px',
  borderRadius: '4px',
  display: 'inline',
}));

export default inject('datastore')((props: {datastore?: DataStore }) => {
  const { game } = props.datastore!;
  const explainer = game?.myRole === PlayerRole.EXPLAINER ? <You>Вы</You> : game?.explainer;
  const guesser = game?.myRole === PlayerRole.GUESSER ? <You>Вы</You> : game?.guesser;
  return <Card>
    <Typography className="centered" variant="h6">
      {explainer}&nbsp;&nbsp;&nbsp; >>> &nbsp;&nbsp;&nbsp;{guesser}
    </Typography>
  </Card>
});
