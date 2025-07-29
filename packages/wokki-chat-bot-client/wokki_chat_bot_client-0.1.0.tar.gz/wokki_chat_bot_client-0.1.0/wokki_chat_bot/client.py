import socketio

class WokkiChatBot:
    def __init__(self, bot_token: str, server_id=None, command_handler=None):
        self.bot_token = bot_token
        self.server_id = server_id
        self.sio = socketio.Client()
        self.sio.on('connect', self.on_connect)
        self.sio.on('error', self.on_error)
        self.connected = False
        self.sio.on('send_bot_message_response', self.on_send_response)
        self.sio.on('bot_command_received', self.on_bot_command_received)
        self.command_handler = command_handler

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

    def send_message(self, channel_id: str, message: str, server_id: str):
        if not self.connected:
            print("Not connected! Call connect() first.")
            return
        self.sio.emit('send_bot_message', {
            'message': message,
            'server_id': server_id,
            'channel_id': channel_id,
            'bot_token': self.bot_token
        })
    def on_send_response(self, data):
        print("Response to send_bot_message:", data)

    def on_bot_command_received(self, data):
        print("Bot command received:", data)
        if self.command_handler:
            self.command_handler(data)

    def respond_to_command(self, channel_id: str, response_msg: str, command: str, user_id: str, server_id: str):
        self.sio.emit('send_bot_message', {
            'command': command,
            'message': response_msg,
            'server_id': server_id,
            'channel_id': channel_id,
            'bot_token': self.bot_token,
            'user_id': user_id
        })
        
    def initialize_commands(self, commands: list):
        self.sio.emit('initialize_commands', {
            'commands': commands,
            'bot_token': self.bot_token
        })