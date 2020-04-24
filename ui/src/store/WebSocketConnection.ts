import {action, observable} from 'mobx';

export enum ConnectionStatus {
  Disconnected = "Disconnected",
  Connecting = "Connecting",
  Retrying = "Retrying",
  Established = "Established"
}

const MAX_RECONNECT_ATTEMPTS = 10;

export default class WebSocketConnection {
    @observable connectionStatus = ConnectionStatus.Disconnected;
    private ws: WebSocket | null = null;
    private reconnectAttempt = 0;
    private receivers: ((data: any) => void)[] = [];
    private readonly id: string;

    constructor(id: string) {
      this.id = id;
    }

    @action establishConnection = () => {
      if (this.ws) {
        this.disconnect();
      }
      this.reconnectManually();
    };

    @action.bound reconnect = () => {
      this.connectionStatus = ConnectionStatus.Connecting;
      const wsProto = window.location.protocol === 'https' ? 'wss' : 'ws';
      const wsUri = process.env.NODE_ENV === 'development'
        ? `ws:${window.location.hostname}:8088/ws/${this.id}`
        : `${wsProto}:${window.location.host}/ws/${this.id}`;
      this.ws = new WebSocket(wsUri);
      this.ws.addEventListener('open', this.onOpen);
      this.ws.addEventListener('message', this.onMessage);
      this.ws.addEventListener('close', this.onClose);
      this.ws.addEventListener('error', this.onError);
    };

    @action disconnect = () => {
      if (this.ws) {
        this.ws.removeEventListener('open', this.onOpen);
        this.ws.removeEventListener('message', this.onMessage);
        this.ws.removeEventListener('close', this.onClose);
        this.ws.removeEventListener('error', this.onError);
        this.ws.close();
        this.connectionStatus = ConnectionStatus.Disconnected;
        this.ws = null;
      }
    };

    onMessage = (event: any) => {
      const data = JSON.parse(event.data);
      this.sendToSubscribers(data);
    };

    sendToSubscribers = (data: any) => {
      for (const receiver of this.receivers) {
        try {
          receiver(data);
        } catch (err) {
          console.error('Error when handling websocket message:', err);
        }
      }
    };

    @action onOpen = (): void => {
      this.connectionStatus = ConnectionStatus.Established;
      this.sendToSubscribers(null);
    };

    @action onClose = (event: any) => {
      if (!event.wasClean) {
        console.error('WebSocket error:', event.code, event.reason);
        if (this.reconnectAttempt < MAX_RECONNECT_ATTEMPTS) {
          ++this.reconnectAttempt;
          setTimeout(this.reconnect, 2000);
          this.connectionStatus = ConnectionStatus.Retrying;
        } else {
          this.connectionStatus = ConnectionStatus.Disconnected;
        }
      }
    };

    onError = (event: any) => {
      console.log('WebSocket error: ', event);
    };

    reconnectManually = (): void => {
      this.reconnectAttempt = 0;
      this.reconnect();
    };

    send = (data: any) => {
      this.ws!.send(JSON.stringify(data));
    };

    // Subscribe to be sent all messages received on websocket.
    // Every subscriber also gets a `null` at connection (re)start.
    subscribeReceiver = (receiver: (data: any) => void) => {
      this.receivers.push(receiver);
    };

    unsubscribeReceiver = (receiver: (data: any) => void) => {
      this.receivers = this.receivers.filter(r => r !== receiver);
    };
}