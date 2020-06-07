import React from "react";
import { Box, styled } from '@material-ui/core';

export const DrawerContents = styled(Box)({
    width: '60vw',
    maxWidth: '400px',
    minWidth: '230px',
});

export const Title = styled(Box)(({ theme }) => ({
    height: '40px',
    padding: '10px 24px',
    color: theme.palette.primary.contrastText,
    backgroundColor: theme.palette.primary.main,
    display: 'flex',
    alignItems: 'center',
}));

export const BottomPad = styled(Box)(({ theme }) => ({
    height: '40px',
    padding: '10px 24px',
    backgroundColor: theme.palette.background.paper,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    boxShadow: '0 0 4px',
}));
