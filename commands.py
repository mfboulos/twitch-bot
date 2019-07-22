from enum import Enum, auto
from datetime import datetime, timedelta

class Permission(Enum):
    USER = auto()
    SUB = auto()
    MOD = auto()
    ADMIN = auto()

class Command(object):
    def __init__(self, permission=Permission.USER):
        self.permission = permission

class ExecutedCommand(Command):
    def __init__(self, command, permission=Permission.USER):
        super().__init__(permission)
        self.command = command
    
    def _parse_message(self, message):
        tokens = message.split()
        return (tokens[0], tokens[1:])
    
    def match(self, message):
        return self._parse_message(message)[0] is self.command
    
    def run(self, tokens):
        pass

class TimedCommand(Command):
    def __init__(self,
                 min_messages=5,
                 interval=300,
                 permission=Permission.USER,
                 message='COGGERS'):
        super().__init__(permission)
        self.min_messages = min_messages
        self.interval = interval
        self._message = message

        self._num_messages = 0
        self.base_time = datetime.now()
    
    def _ready(self):
        message_check = self._num_messages >= self.min_messages
        time_check = datetime.now() - self.base_time > timedelta(seconds=self.interval)
        return message_check and time_check
    
    def process_message(self):
        self._num_messages += 1
    
    def get_message(self):
        return self._message if self._ready() else None