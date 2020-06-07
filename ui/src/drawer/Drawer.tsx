import React from 'react';
import { Drawer } from '@material-ui/core';
import { inject, observer } from 'mobx-react';

import DataStore from 'store/DataStore';
import UIStore from 'store/UIStore';

import { GameState } from 'store/types';
import UnstartedDrawer from 'drawer/UnstartedDrawer';

interface CommonDrawerProps {
    datastore?: DataStore;
    uistore?: UIStore;
}

export default inject('datastore', 'uistore')(observer((props: CommonDrawerProps) => {
    const { uistore, datastore } = props;
    let drawerContent: React.ReactElement | undefined;
    if (datastore!.game?.gameState === GameState.SETUP) {
        drawerContent = <UnstartedDrawer />;
    } else {
        return null;
    }

    return <Drawer open={uistore!.drawerOpen} onClose={() => uistore!.setDrawerOpen(false)}>
        {drawerContent}
    </Drawer>;
}));