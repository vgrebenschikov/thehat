import {
    AppBar,
    Avatar,
    Button,
    createStyles,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    IconButton,
    Theme,
    Toolbar,
    Typography,
    withStyles
} from "@material-ui/core";
import {makeStyles} from "@material-ui/core/styles";
import {inject, observer} from "mobx-react";
import React, {createRef} from "react";
import DataStore from "./store/DataStore";
import UIStore from "./store/UIStore";
import GoogleLogin from "react-google-login";
import loginConfig from "login-config";

const styles = (theme: Theme) => createStyles({
    menuButton: {
        marginRight: theme.spacing(2),
    },
    title: {
        flexGrow: 1,
    },
    // We need to hide the element which displays URL to be copied (for sharing),
    // but the browser will not copy anything that is not visible; so we just
    // make the input hang somewhere far far away... (insert bitter CSS joke).
    hidden: {
        position: 'absolute',
        left: '-1000px',
        top: '-1000px',
    }
});
const useStyles = makeStyles(styles);

const UserDesignator = inject("datastore")(observer((props: { datastore?: DataStore }) => {
    const {datastore} = props;
    if (!datastore!.user) {
        return null;
    }
    const name = datastore!.user.name;
    const picture = datastore?.user.imageUrl;
    return picture ? <Avatar alt={name} src={picture}/> : <Avatar alt={name}>?</Avatar>;
}));

const LoginDialog = inject("datastore")(observer((props: { datastore?: DataStore }) => {
    const {datastore} = props;
    return <Dialog open={!datastore?.user}>
        <DialogTitle>Будем знакомы</DialogTitle>
        <DialogContent>
            <DialogContentText>
                Чтобы играть в Шляпу, необходимо представиться
            </DialogContentText>
            <DialogActions>
                <GoogleLogin
                    clientId={loginConfig.googleClientId}
                    buttonText="Войти"
                    onSuccess={datastore!.signIn}
                    onFailure={datastore!.signIn}
                    isSignedIn={true}
                    render={props => (
                        <Button onClick={props.onClick} variant="contained" disabled={props.disabled}>Войти через Google</Button>
                    )}
                    cookiePolicy={'single_host_origin'}/>
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
                       onClick={() => props.uistore?.setDrawerOpen(true)}
    >
        <i className="material-icons-round">menu</i>
    </IconButton>
}));

@inject('uistore')
@observer
class _ShareButton extends React.Component<{classes: any, uistore?: UIStore}, {}> {
    inputref = createRef<HTMLInputElement>();

    share = () => {
        const {beginShowingSharedConfirmation} = this.props.uistore!;
        if (this.inputref?.current) {
            const elt = this.inputref.current;
            elt.focus();
            elt.select();
            document.execCommand('copy');
            beginShowingSharedConfirmation();
        }
    };

    render() {
        const {classes} = this.props;
        return <>
            <IconButton edge="start"
                        className={classes.menuButton}
                        color="inherit"
                        aria-label="share"
                        onClick={this.share}
            >
                <i className="material-icons-round">share</i>
            </IconButton>
            <input className={classes.hidden} ref={this.inputref} value={window.location.href} readOnly/>
        </>;

    }
}

const ShareButton = withStyles(styles)(_ShareButton);

const NormalTopBar = inject('datastore')(observer((props: { datastore?: DataStore }) => {
    const classes = useStyles();
    const game = props.datastore!.game;
    return <>
            {props.datastore?.game && <MenuButton/>}
            <Typography variant="h6" className={classes.title}>
                {game?.gameName ? `Комната: ${game.gameName}` : "Шляпа!"}
            </Typography>
            {props.datastore?.game && <ShareButton/>}
            <UserDesignator/>
            <LoginDialog/>
    </>;
}));

export default inject('uistore')(observer((props: { uistore?: UIStore }) => {
    const uiStore = props.uistore!;
    return <AppBar position="static">
        <Toolbar>
            {uiStore.showSharedConfirmation
                ? <Typography variant="h6">Ссылка скопирована</Typography>
                : <NormalTopBar/>}
        </Toolbar>
    </AppBar>;
}));