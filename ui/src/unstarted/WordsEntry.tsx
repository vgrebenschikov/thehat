import React from "react";
import {observable} from "mobx";
import {inject, observer} from "mobx-react";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Input,
  styled,
} from "@material-ui/core";

import DataStore from "store/DataStore";
import {DialogStore} from "common/DialogStore";

import {Card} from "common/Card";

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
}

@inject('datastore')
@observer
class AddButton extends React.Component<{ datastore?: DataStore }, {}> {
  submit = () => {
    this.ds.word = this.ds.word.toLowerCase().replace(/^\S/, l => l.toUpperCase())
    this.props.datastore!.addOwnWord(this.ds.word);
  };

  ds: AddWordDialogStore = new AddWordDialogStore(this.submit);

  render() {
    return <Card>
      <Button className="full-width-button" onClick={this.ds.open}><i className="material-icons-round">add</i></Button>
      <Dialog open={this.ds.isOpen} onClose={this.ds.close}>
        <DialogTitle>Введите новое слово</DialogTitle>
        <form onSubmit={(ev) => {
          ev.preventDefault();
          this.ds.submit()
        }}>
          <DialogContent>
            <Input onChange={this.ds.change('word')}
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
  bottom: '32px',
  right: '16px',
  boxShadow: '0 0 4px black',
  borderRadius: '24px',
  backgroundColor: theme.palette.secondary.main,
  color: theme.palette.secondary.contrastText,
  height: '48px',
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  '& .button': {
    width: '100%',
    height: '100%',
  },
})) as typeof Box;

const WordList = styled(Box)({
  flexGrow: 1,
  minHeight: 0,
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'flex-start',
  alignItems: 'stretch',
  overflow: 'auto',
  width: '100%',
  padding: '8px 8px 0 8px',
}) as typeof Box;

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
      <WordList>
        {words.map((w) => <WordCard word={w} onDelete={() => this.deleteWord(w)} key={w}/>)}
        {words.length < this.props.datastore!.game!.gameNumWords! && <AddButton/>}
      </WordList>
      <BottomButton>
        <Button className="button" onClick={this.commitWords}><i className="material-icons-round">check</i>Готово</Button>
      </BottomButton>
    </>;
  }
}
