import socketio
import uuid
import threading

class WokkiChatBot:
    def __init__(self, bot_token: str, server_id=None, command_handler=None, button_handler=None):
        self.bot_token = bot_token
        self.server_id = server_id
        self.sio = socketio.Client()
        self.sio.on('connect', self.on_connect)
        self.sio.on('error', self.on_error)
        self.sio.on('send_bot_message_response', self.on_send_response)
        self.sio.on('bot_command_received', self.on_bot_command_received)
        self.sio.on('embed_button_pressed', self.on_button_click_received)
        self.connected = False
        self.command_handler = command_handler
        self.button_handler = button_handler
        self._response_futures = {}

    def on_connect(self):
        print("Connected to server")
        self.connected = True

    def on_error(self, data):
        print("Server error:", data)

    def connect(self):
        url = f"https://chat.wokki20.nl?bot_token={self.bot_token}{f'&server_id={self.server_id}' if self.server_id else ''}"
        self.sio.connect(url, socketio_path='/socket.io', transports=['websocket'])

    def disconnect(self):
        if self.connected:
            self.sio.disconnect()
            self.connected = False
            print("Disconnected from server")

    def _create_future(self):
        event = threading.Event()
        return {"event": event, "data": None}

    def on_send_response(self, data):
        print("Response to send_bot_message:", data)
        req_id = data.get('req_id')
        if req_id and req_id in self._response_futures:
            self._response_futures[req_id]["data"] = data
            self._response_futures[req_id]["event"].set()

    def send_message(self, channel_id: str, message: str, server_id: str, return_response=False):
        if not self.connected:
            print("Not connected! Call connect() first.")
            return None

        payload = {
            'message': message,
            'server_id': server_id,
            'channel_id': channel_id,
            'bot_token': self.bot_token
        }

        if return_response:
            req_id = str(uuid.uuid4())
            future = self._create_future()
            self._response_futures[req_id] = future
            payload["req_id"] = req_id

            self.sio.emit('send_bot_message', payload)

            future["event"].wait(timeout=5)
            return self._response_futures.pop(req_id, {}).get("data")

        else:
            self.sio.emit('send_bot_message', payload)
            return None



    def respond_to_command(self, channel_id: str, response_msg: str, command: str, user_id: str, server_id: str, embed=None, return_response=False):
        payload = {
            'command': command,
            'message': response_msg,
            'server_id': server_id,
            'channel_id': channel_id,
            'bot_token': self.bot_token,
            'user_id': user_id,
            'embed': embed
        }

        if return_response:
            req_id = str(uuid.uuid4())
            future = self._create_future()
            self._response_futures[req_id] = future
            payload["req_id"] = req_id
        else:
            req_id = None
            future = None

        self.sio.emit('send_bot_message', payload)

        if return_response and future:
            future["event"].wait(timeout=5)
            return self._response_futures.pop(req_id, {}).get("data")
        return None



    def edit_message(self, message_id: str, message=None, embed=None, return_response=False):
        req_id = str(uuid.uuid4()) if return_response else None
        payload = {
            'message_id': message_id,
            'message': message,
            'embed': embed,
            'bot_token': self.bot_token
        }

        future = None
        if return_response:
            payload["req_id"] = req_id
            future = self._create_future()
            self._response_futures[req_id] = future

        self.sio.emit('edit_bot_message', payload)

        if return_response and future:
            future["event"].wait(timeout=5)
            return self._response_futures.pop(req_id, {}).get("data")
        return None

    def on_bot_command_received(self, data):
        print("Bot command received:", data)
        if self.command_handler:
            self.command_handler(data)

    def on_button_click_received(self, data):
        print("Button click received:", data)
        if self.button_handler:
            self.button_handler(data)

    def initialize_commands(self, commands: list):
        self.sio.emit('initialize_commands', {
            'commands': commands,
            'bot_token': self.bot_token
        })
