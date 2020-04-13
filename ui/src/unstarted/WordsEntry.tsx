import {action, observable} from "mobx";
import {inject, observer} from "mobx-react";
import React from "react";
import {
  Box,
  Button,
  createStyles,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Input,
  Paper,
  styled,
  Theme,
  withStyles
} from "@material-ui/core";
import DataStore from "store/DataStore";
import {DialogStore} from "common/DialogStore";

const styles = (theme: Theme) => createStyles({
  button: {
    margin: theme.spacing(2),
  },
});

const Card = styled(Paper)(({theme}) => ({
  padding: '16px',
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
  },
  '& .icon': {
    flexGrow: 0,
  }
})) as typeof Paper;

interface WordCardProps {
  word: string,
  onDelete: () => void,
}

@observer
class WordCard extends React.Component<WordCardProps, {}> {
  render() {
    return <Card>
      <div className="content">{this.props.word}</div>
      <IconButton className="icon" onClick={this.props.onDelete}><i
        className="material-icons-round">delete</i></IconButton>
    </Card>;
  }
}

class AddWordDialogStore extends DialogStore {
  @observable word: string = '';

  @action.bound
  setWord(w: string) {
    this.word = w;
  }
}

@inject('datastore')
@observer
class AddButton extends React.Component<{ datastore?: DataStore }, {}> {
  submit = () => {
    this.props.datastore!.addOwnWord(this.ds.word);
  };

  ds: AddWordDialogStore = new AddWordDialogStore(this.submit);

  render() {
    return <Card>
      <Button className="content" onClick={this.ds.open}><i className="material-icons-round">add</i></Button>
      <Dialog open={this.ds.isOpen} onClose={this.ds.close}>
        <DialogTitle>Введите новое слово</DialogTitle>
        <form onSubmit={(ev) => {
          ev.preventDefault();
          this.ds.submit()
        }}>
          <DialogContent>
            <Input onChange={ev => this.ds.setWord(ev.target.value)}
                   autoFocus>{this.ds.word}</Input>
          </DialogContent>
          <DialogActions>
            <Button onClick={this.ds.close}>Отмена</Button>
            <Button type="submit">OK</Button>
          </DialogActions>
        </form>
      </Dialog>
    </Card>;
  }
}


const BottomButton = styled(Box)(({theme}) => ({
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
  '& .button': {
    width: '100%',
    height: '100%',
  },
})) as typeof Paper;

@inject('datastore')
@observer
export default class WordsEntry extends React.Component<{datastore?: DataStore}, {}> {
  deleteWord = (w: string) => {
    this.props.datastore!.deleteOwnWord(w);
  };

  commitWords = () => {
    this.props.datastore!.sendWords();
  };

  render() {
    const words = this.props.datastore!.ownWords;
    return <>
      {words.map((w) => <WordCard word={w} onDelete={() => this.deleteWord(w)} key={w}/>)}
      <AddButton/>
      <BottomButton>
        <Button className="button" onClick={this.commitWords}><i className="material-icons-round">check</i>Готово</Button>
      </BottomButton>
    </>;
  }
}
