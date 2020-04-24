import {
    AppBar,
    Avatar,
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    IconButton,
    Theme,
    Toolbar,
    Typography
} from "@material-ui/core";
import {makeStyles} from "@material-ui/core/styles";
import {inject, observer} from "mobx-react";
import React from "react";
import DataStore from "./store/DataStore";
import UIStore from "./store/UIStore";

const styles = (theme: Theme) => ({
    menuButton: {
        marginRight: theme.spacing(2),
    },
    title: {
        flexGrow: 1,
    },
});
const useStyles = makeStyles(styles);

const UserDesignator = inject("datastore")(observer((props: { datastore?: DataStore }) => {
    const { datastore } = props;
    if (!datastore?.user) {
        return null;
    }
    const name = datastore.userName;
    const picture = datastore?.user.photoURL;
    return picture ? <Avatar alt={name} src={picture} /> : <Avatar alt={name}>?</Avatar>;
}));

const LoginDialog = inject("datastore")(observer((props: { datastore?: DataStore }) => {
    const { datastore } = props;
    return <Dialog open={!datastore?.user}>
        <DialogTitle>Log in required</DialogTitle>
        <DialogContent>
            <DialogContentText>
                Logging in is required to use Cotify.
            </DialogContentText>
            <DialogActions>
                <Button variant="contained" onClick={datastore?.signIn}>Sign in with Google</Button>
            </DialogActions>
            {datastore?.loginError && <Typography variant="body2" color="error">{datastore.loginError}</Typography>}
        </DialogContent>
    </Dialog>
}));

const MenuButton = inject('uistore')(observer((props: { uistore?: UIStore }) => {
    const classes = useStyles();
    return <IconButton edge="start"
                       className={classes.menuButton}
                       color="inherit"
                       aria-label="menu"
                       onClick={()=>props.uistore?.setDrawerOpen(true)}
    >
        <i className="material-icons-round">menu</i>
    </IconButton>
}));

export default inject('datastore')(observer((props: { datastore?: DataStore }) => {
    const classes = useStyles();
    const game = props.datastore!.game;
    return <AppBar position="static">
        <Toolbar>
            {props.datastore?.game && <MenuButton/>}
            <Typography variant="h6" className={classes.title}>
                {game?.gameName ? `Комната: ${game.gameName}` : "Шляпа!"}
            </Typography>
            <UserDesignator />
        </Toolbar>
        <LoginDialog />
    </AppBar>;
}));