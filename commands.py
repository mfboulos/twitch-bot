from twisted.words.protocols.irc import IRCClient
from datetime import datetime, timedelta
from enum import Enum, auto

import random
import re

class Permission(Enum):
    USER = auto()
    SUB = auto()
    MOD = auto()
    ADMIN = auto()

class Rule(object):
    def run(self, user, message):
        """
        Runs something based on the message and user.
        """
        raise NotImplementedError
    
class Command(Rule):
    def __init__(self,
                 bot,
                 name,
                 response=None,
                 permission=Permission.USER)
        self._bot = bot
        self.name = name
        self.response = response
        self.permission = permission

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
    
    def run(self, user, message):
        """
        Processes `message`, builds a response using `self.response`, and
        outputs it using the bot.
        """

        if self._match(message) and self.response:
            self._bot.write(self.response)

class TimedRule(Rule):
    def __init__(self,
                 bot,
                 min_messages=5,
                 interval=300,
                 pattern=None):
        self._bot = bot
        self.min_messages = min_messages
        self.interval = interval
        self.pattern = pattern

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
    
    def run(self, user, message):
        """
        Makes the bot write this command's message if the command is ready
        """

        self.__num_messages += 1
        if self._ready:
            self._bot.write(self.message)
            self.__num_messages = 0

class RollCommand(ExecutedCommand):
    def __init__(self, bot: IRCClient):
        super().__init__(bot, '!roll')
    
    def _parse_message(self, message):
        exec_token, args = super()._parse_message(message)
        match = re.search('(\d+)d(\d+)', args[0]) if args else None
        if match:
            return exec_token, int(match.group(1)), int(match.group(2))
        else:
            return exec_token, None, None

    def _match(self, message):
        return all(self._parse_message(message))
    
    def run(self, user, channel, message):
        if self._match(message):
            exec_token, amount, dice_faces = self._parse_message(message)
            amount = max(1, min(100, amount))
            dice_faces = max(1, min(100, dice_faces))

            total = 0
            for _ in range(amount):
                total += random.randint(1, dice_faces)
            
            response = '/me @%s rolling %dd%d: %d' % (user, amount, dice_faces, total)
            if total is amount:
                response += ' LUL'
            elif total is amount * dice_faces:
                response += ' PogChamp'
            self._bot.say(channel, response)