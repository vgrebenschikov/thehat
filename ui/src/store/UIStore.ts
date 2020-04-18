import {action, observable} from "mobx";

export default class UIStore {
  @observable drawerOpen: boolean = false;
  @observable tourDialogOpen: boolean = false;

  @action.bound setDrawerOpen(state: boolean) {
    this.drawerOpen = state;
  }

  @action.bound setTourDialogOpen(state: boolean) {
    this.tourDialogOpen = state;
  }
}