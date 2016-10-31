'use strict';
class io {
	constructor(address) {
		this.socket = new WebSocket(address);
		this.handlers = {};  // event -> callback
		this.ack_callbacks = {};  // message id -> callback

		this.socket.onmessage = this._onmessage.bind(this);
		this.socket.onerror = this._onerror.bind(this);
		this.socket.onopen = this._onopen.bind(this);
		this.socket.onclose = this._onclose.bind(this);

		this.next_id = 0;
	}
	_onmessage(ws_event) {
		console.debug("onmessage", ws_event);
		let message;
		try {
			message = JSON.parse(ws_event.data);
		}
		catch (e) {
			console.error("cannot parse message", e);
			return;
		}
		let type = message.type;
		let id = message.id;
		let event = message.event;
		let data = message.data;
		switch (type) {
		case "EVENT":
			this._handle_event(id, event, data);
			break;
		case "ACK":
			let ack_callback = this.ack_callbacks[id];
			delete this.ack_callbacks[id];
			if (ack_callback !== undefined)
				ack_callback(data);
			break;
		default:
			console.error("unknown message type", type);
		}
	}
	_onerror(ws_event) {
		console.debug("onerror", ws_event);
		this._handle_event(undefined, "error");
	}
	_onopen(ws_event) {
		console.debug("onopen", ws_event);
		this._handle_event(undefined, "connect");
	}
	_onclose(ws_event) {
		console.debug("onclose", ws_event);
		this._handle_event(undefined, "disconnect");
	}
	_handle_event(id, event, data) {
		let handler = this.handlers[event];
		if (handler === undefined) {
			console.info(`no handler for '${event}'`);
			return;
		}
		console.debug(`call '${event}' handler`);
		let ack;
		if (id === undefined) {
			ack = () => {};
		}
		else {
			ack = (ack_data) => {this._send_ack(id, ack_data)};
		}
		handler(data, ack);
	}
	_send_message(message) {
		let message_str = JSON.stringify(message);
		this.socket.send(message_str);
	}
	_send_ack(message_id, data) {
		let message = {type: "ACK", id: message_id};
		if (data !== undefined && data !== null)
			message.data = data;
		this._send_message(message);
	}
	emit(event, data, callback) {
		console.debug("emit", event, data);
		let message = {type: "EVENT", event: event};
		if (data !== undefined && data !== null)
			message.data = data;
		if (callback !== undefined) {
			message.id = this.next_id;
			++this.next_id;
			this.ack_callbacks[message.id] = callback;
		}
		this._send_message(message);
	}
	on(event, callback) {
		console.debug(`register '${event}' handler`);
		this.handlers[event] = callback;
	}
}
