import React from "react";
import {Paper, styled} from "@material-ui/core";
import {Card} from "common/Card";

const MessagePaper = styled(Card)(({theme}) => ({
  padding: theme.spacing(2),
  alignContent: 'center',
  margin: 'auto',
  boxShadow: '0 0 4px',
})) as typeof Paper;

export const PleaseWait = () => {
  return <MessagePaper>
    Ожидайте своего хода
  </MessagePaper>
};