import React from "react";
import UIStore from "store/UIStore";
import DataStore from "store/DataStore";
import { Dialog, DialogTitle, DialogContent, DialogActions, DialogContentText, Button } from "@material-ui/core";

import tourDescription from "tourDescription";
import { inject, observer } from "mobx-react";

export default inject('datastore', 'uistore')(observer((props: {datastore?: DataStore, uistore?: UIStore}) => {
    if (!props.datastore!.game) {return null}
    const {tourDialogOpen, setTourDialogOpen} = props.uistore!;
    const {tourNumber} = props.datastore!.game;
    return <Dialog open={tourDialogOpen} onClose={() => setTourDialogOpen(false)}>
        <DialogTitle>Смена тура</DialogTitle>
        <DialogContent>
            <DialogContentText>
                {tourDescription[tourNumber!]}
            </DialogContentText>
        </DialogContent>
        <DialogActions>
            <Button onClick={()=>setTourDialogOpen(false)}>Да!</Button>
        </DialogActions>
    </Dialog>
}));