from twisted.words.protocols.irc import IRCClient

from neomodel import StructuredNode, StringProperty, IntegerProperty, DateTimeProperty, RelationshipFrom, RelationshipTo
from neomodel.cardinality import One, OneOrMore

from datetime import datetime, timedelta
from enum import Enum, auto

from relationships import CommandUseRel

import random
import re

class Identifier(Enum):
    USER = 'user'
    ARG = 'arg'
    RANDOM = 'random'

class Rule(object):
    def run(self, user, message):
        """
        Runs something based on a message and user.
        
        :param user: 
        :type user: str
        :param message:
        :type message: str
        :raises NotImplementedError:
        """
        raise NotImplementedError

class Command(Rule, StructuredNode):
    response = StringProperty()
    bots = RelationshipFrom('bot.TwitchBot', 'CAN_USE', cardinality=OneOrMore,
                           model=CommandUseRel)
    owner = RelationshipFrom('bot.TwitchBot', 'OWNS', cardinality=One)

    def __init__(self, response=None, *args, **kwargs):
        kwargs['response'] = response
        
        self.__sep = '|'

        super().__init__(*args, **kwargs)
    
    def _parse_message(self, message):
        """
        Parse a message into what would be read as the execution token and its
        arguments separately.

        Returns a tuple pair of the potential execution token and its list of
        respective arguments.
        """

        return tuple(message.split())
    
    # TODO: move to bot
    def _match(self, message):
        """
        Returns `True` if the message's execution token matches the name of the
        command, `False` otherwise.
        """
        pass
        # return self._parse_message(message)[0] is self.name

    def __build_response(self, user, message):
        """
        Builds the response to a message with reference to several format
        specifiers.
        """
        
        response = self.response
        bracket_stack = []
        pairs = []

        idx = 0
        while idx < len(response):
            c = response[idx]
            if c is '{':
                bracket_stack.append(idx)
            elif c is '}':
                try:
                    start = bracket_stack.pop()
                    placeholder = response[start:idx + 1]
                    replacement = self.__process_placeholder(placeholder,
                                                             user,
                                                             message)
                    response = response.replace(placeholder, replacement)
                    idx = start + len(replacement) - 1
                except IndexError:
                    print('No open bracket for the closed bracket at index {}!'.format(idx))
            idx += 1
        
        if bracket_stack:
            print('No closed bracket for open bracket(s) at: {}'.format(bracket_stack))
        
        return response
        
    def __process_placeholder(self, placeholder, user, message):
        tokens = message.split()
        contents = placeholder[1:-1] if re.match('^\{.+\}$', placeholder) else placeholder
        parts = contents.split(self.__sep)

        try:
            identifier = Identifier(parts[0])

            if identifier is Identifier.USER:
                return user
            elif identifier is Identifier.ARG:
                return tokens[int(parts[1].split()[0])]
            elif identifier is Identifier.RANDOM:
                return random.choice(parts[1].split())
        except Exception:
            return placeholder

    # TODO: rewrite to take either bot or write function
    def run(self, user, message):
        """
        Processes `message`, builds a response using `self.response`, and
        outputs it using the bot.
        """

        if self._match(message) and self.response:
            self._write(self.__build_response(response))

class TimedRule(Rule, StructuredNode):
    response = StringProperty()
    min_messages = IntegerProperty(default=5)
    num_messages = IntegerProperty(default=0)
    cooldown = IntegerProperty(default=300)
    last_called = DateTimeProperty(default_now=datetime.now)
    bots = RelationshipFrom('bot.TwitchBot', 'CAN_USE', cardinality=OneOrMore,
                           model=CommandUseRel)
    owner = RelationshipFrom('bot.TwitchBot', 'OWNS', cardinality=One)

    def __init__(self, response=None, *args, **kwargs):
        kwargs['response'] = response
        super().__init__(*args, **kwargs)
    
    @property
    def _ready(self):
        """
        Determines whether this rule is ready to be executed again.
        
        :return:
        :rtype: bool
        """

        message_check = self.num_messages >= self.min_messages
        time_check = datetime.now() - self.last_called > timedelta(seconds=self.intecooldownrval)
        return message_check and time_check
    
    # TODO: rewrite to take either bot or write function
    def run(self, user, message):
        """
        Makes the bot write this command's message if the command is ready
        """

        self.num_messages += 1
        if self._ready:
            self.num_messages = 0

# I'm just gonna keep this around til I make a roll command with the current framework

# class RollCommand(ExecutedCommand):
#     def __init__(self, bot: IRCClient):
#         super().__init__(bot, '!roll')
    
#     def _parse_message(self, message):
#         exec_token, args = super()._parse_message(message)
#         match = re.search('(\d+)d(\d+)', args[0]) if args else None
#         if match:
#             return exec_token, int(match.group(1)), int(match.group(2))
#         else:
#             return exec_token, None, None

#     def _match(self, message):
#         return all(self._parse_message(message))
    
#     def run(self, user, channel, message):
#         if self._match(message):
#             exec_token, amount, dice_faces = self._parse_message(message)
#             amount = max(1, min(100, amount))
#             dice_faces = max(1, min(100, dice_faces))

#             total = 0
#             for _ in range(amount):
#                 total += random.randint(1, dice_faces)
            
#             response = '/me @%s rolling %dd%d: %d' % (user, amount, dice_faces, total)
#             if total is amount:
#                 response += ' LUL'
#             elif total is amount * dice_faces:
#                 response += ' PogChamp'
#             self._bot.say(channel, response)