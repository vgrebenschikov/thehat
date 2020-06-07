import React from "react";
import { inject, observer } from "mobx-react";
import { Button, Typography } from "@material-ui/core";

import DataStore from "store/DataStore";
import { DrawerContents, Title, BottomPad } from 'drawer/DrawerCards';

export default inject('datastore')(observer((props: { datastore?: DataStore }) => {
    return <DrawerContents>
        <Title>
            <Typography variant="h6">Играем</Typography>
        </Title>
        <BottomPad>
            <Button variant="contained" color="secondary" onClick={props.datastore!.leaveGame}>Покинуть игру</Button>
        </BottomPad>
    </DrawerContents>;
}));
