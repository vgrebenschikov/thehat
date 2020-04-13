import {action, observable} from 'mobx';

enum ConnectionStatus {
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

    @action establishConnection = () => {
      if (this.ws) {
        this.disconnect();
      }
      this.reconnectManually();
    };

    @action reconnect = () => {
      this.connectionStatus = ConnectionStatus.Connecting;
      const wsUri = 'ws:localhost:8088/ws';
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

    subscribeReceiver = (receiver: (data: any) => void) => {
      this.receivers.push(receiver);
    };

    unsubscribeReceiver = (receiver: (data: any) => void) => {
      this.receivers = this.receivers.filter(r => r !== receiver);
    };
}