import {Paper, styled} from "@material-ui/core";

export const Card = styled(Paper)(({theme}) => ({
  padding: '0',
  display: 'flex',
  flexDirection: 'row',
  alignItems: 'center',
  justifyContent: 'stretch',
  marginBottom: '8px',
  boxShadow: '0 0 4px',
  '& .content': {
    fontsize: '24px',
    color: theme.palette.text.primary,
    flexGrow: 1,
    margin: '24px 16px',
  },
  '& .icon': {
    flexGrow: 0,
  },
  '& .full-width-button': {
    margin: 0,
    padding: '16px',
    flexGrow: 1,
  },
  '& .centered': {
    margin: '0 auto',
    padding: '16px',
  }
})) as typeof Paper;

export const MidCard = styled(Card)(({theme}) => ({
  margin: 'auto 0'
})) as typeof Card;
