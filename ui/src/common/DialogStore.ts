import {action, observable} from "mobx";

export class DialogStore {
  @observable isOpen: boolean = false;
  callback: () => void;

  constructor(callback: () => void) {
    this.callback = callback;
  }

  @action.bound
  open() {
    this.isOpen = true;
  }

  @action.bound
  close() {
    this.isOpen = false;
  }

  @action.bound
  submit() {
    this.isOpen = false;
    this.callback();
  }
}