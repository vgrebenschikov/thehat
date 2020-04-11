import {action, observable} from "mobx";

export default class UIStore {
  @observable drawerOpen: boolean = false;

  @action setDrawerOpen(state: boolean) {
    this.drawerOpen = state;
  }
}