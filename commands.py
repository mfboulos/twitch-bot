from datetime import datetime, timedelta
from enum import Enum, auto
from bot import TwitchBot

class Permission(Enum):
    USER = auto()
    SUB = auto()
    MOD = auto()
    ADMIN = auto()

class Command(object):
    def __init__(self,
                 bot: TwitchBot,
                 permission=Permission.USER):
        self._bot = bot
        self.permission = permission
    
    def run(self, message):
        """
        Run the command based on the message.

        Subclasses should override this function.
        """

        pass
    

class ExecutedCommand(Command):
    def __init__(self,
                 bot: TwitchBot,
                 name,
                 response=None,
                 permission=Permission.USER):
        super().__init__(bot, permission=permission)
        self.name = name
        self.response = response
    
    def _parse_message(self, message):
        """
        Parse a message into what would be read as the execution token and its
        arguments separately.

        Returns a tuple pair of the potential execution token and its list of
        respective arguments.
        """

        tokens = message.split()
        return (tokens[0], tokens[1:])
    
    def _match(self, message):
        """
        Returns `True` if the message's execution token matches the name of the
        command, `False` otherwise.
        """

        return self._parse_message(message)[0] is self.name
    
    def run(self, message):
        """
        Processes the message first, then makes the bot say this command's
        response in chat if the message matches the command.
        """

        if self._match(message) and self.response:
            self._bot.write(self.response)

class TimedCommand(Command):
    def __init__(self,
                 min_messages=5,
                 interval=300,
                 permission=Permission.USER,
                 message='COGGERS'):
        super().__init__(permission)
        self.min_messages = min_messages
        self.interval = interval
        self.message = message

        self.__num_messages = 0
        self.base_time = datetime.now()
    
    @property
    def _ready(self):
        """
        Returns `True` if this command is ready to execute again, `False` otherwise
        """

        message_check = self.__num_messages >= self.min_messages
        time_check = datetime.now() - self.base_time > timedelta(seconds=self.interval)
        return message_check and time_check
    
    def run(self):
        """
        Makes the bot write this command's message if the command is ready
        """

        self.__num_messages += 1
        if self._ready:
            self._bot.write(self.message)
            self.__num_messages = 0