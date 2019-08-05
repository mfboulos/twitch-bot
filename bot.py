from neomodel import StructuredNode, StringProperty, ArrayProperty, RelationshipTo, RelationshipFrom
from neomodel.exceptions import UniqueProperty, DoesNotExist
from neomodel.cardinality import One

from twisted.words.protocols.irc import IRCClient
from twisted.internet import reactor

from placeholder_ops import UserOp, ArgsOp, RandomOp
from relationships import CommandUseRel
from commands import Command

from json import JSONEncoder, JSONDecoder
from typing import List

import requests
import pickle
import typing
import socket
import atexit
import json
import re
import os

USERLIST_API = 'http://tmi.twitch.tv/group/user/{}/chatters'

class BotProtocol(IRCClient, StructuredNode):
    nickname = StringProperty(unique_index=True, required=True)
    bots = RelationshipTo('TwitchBot', 'PROVIDES_IRC_FOR')

    def __init__(self,
                 nickname,
                 factory=None):
        self.nickname = nickname
        self.factory = factory

        self.password = os.environ['TWITCH_OAUTH']

    def signedOn(self):
        self.factory.wait_time = 1

        for bot in bots:
            self.join(bot.channel)

    def joined(self, channel):
        self.say(channel, 'Hello @%s!' % channel)

    def privmsg(self, user, channel, message):
        self.say(channel, 'Nice!')
    
    def left(self, channel):
        self.say(channel, 'Bye!')
    
    def add_bot(self, channel):
        """
        Creates a bot connected to channel and saves it to Neo4j with a
        relationship to this protocol.

        :param channel:
        :type channel: str
        :return: `True` if a bot was made successfully, `False` otherwise
        :rtype: bool
        """
        bot = bots.match(channel=channel_no_prefix(channel)).first_or_none()
        if bots:
            # TODO: log bot already exists
            return False
        
        bot = TwitchBot().save()
        self.bots.connect(bot, {'channel': channel_no_prefix(channel)})
        return True
    
    def remove_bot(self, channel):
        """
        Removes a bot related by the given channel from Neo4j entirely, along
        with all its relationships to any other nodes.

        :param channel:
        :type channel: str
        :return: `True` if a bot was deleted successfully, `False` otherwise
        :rtype: bool
        """
        try:
            self.bots.match(channel=channel_no_prefix(channel)).first().delete()
            return True
        except DoesNotExist:
            # TODO: log bot does not exist
            return False

    @classmethod
    def channel_no_prefix(self, channel):
        """
        Removes prefix from channel name, if it has one.
        
        :param channel:
        :type channel: str
        :return: channel name without prefix
        :rtype: str
        """
        return channel[1:] if channel[0] in '&#!+' else channel

    @classmethod
    def channel_with_prefix(self, channel):
        """
        Adds `#` prefix to channel name.
        
        :param channel: 
        :type channel: str
        :return: channel name with `#` prefix
        :rtype: str
        """
        return '#' + channel_no_prefix(channel)

class TwitchBot(StructuredNode):
    ignore = ArrayProperty(base_property=StringProperty())
    usable_commands = RelationshipTo('Command', 'CAN_USE', model=CommandUseRel)
    owned_commands = RelationshipTo('Command', 'OWNS')
    protocol = RelationshipFrom('BotProtocol', 'PROVIDES_IRC_FOR', cardinality=One)

    def __init__(self,
                 ignore=['nightbot', 'moobot', 'streamelements', '.+bot']):
        kwargs['ignore'] = ignore

        user_data = requests.get(USERLIST_API.format(self.channel)).json()
        chatters = user_data['chatters']

        self.users = set(sum(chatters.values(), []))
        self.mods = set(chatters['moderators'])
        self.subs = set()

        super().__init__(*args, **kwargs)
    
    @property
    def channel(self):
        return protocol.relationship(self).channel

    @property
    def _max_lines(self):
        """
        Returns the max amount of lines that can be written by one command
        execution.
        
        :return: max lines
        :rtype: int
        """
        return 5

    def write(self, message):
        """
        Writes `message` line by line up to `_max_lines`
        
        :param message: 
        :type message: str
        """
        for line in message.split('\n')[:5]:
            self.protocol.single().say(self.channel, line)
    
    # The bot is responsible for building responses stored within a command

    class Placeholder(Enum):
        user = UserOp
        args = ArgsOp
        random = RandomOp

        def process(self, parts, user, message):
            self.value().process(parts, user, message)

    @property
    def sep(self):
        return '|'

    def __build_response(self, user, message, command_response):
        """
        Builds the response to a command invocation.
        
        :param user: username invoking the command
        :type user: str
        :param message: full message of the user invoking the command
        :type message: str
        :param command_response: response structure as defined by a `Command`
        :type command_response: str
        :return: fully built response
        :rtype: str
        """
        response = command_response
        bracket_stack = []

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
        """
        Parses a placeholder from `Command` response structure and returns
        its replacement.

        Returns `placeholder` if it runs into an `Exception` on the way.
        
        :param placeholder: (ex: `{user})
        :type placeholder: str
        :param user: username invoking the command
        :type user: str
        :param message: full message of the user invoking the command
        :type message: str
        :return: replacement for the input `placeholder`
        :rtype: str
        """
        contents = placeholder[1:-1] if re.match('^\{.+\}$', placeholder) else placeholder
        parts = re.split('\s*{}\s*'.format(self.sep), contents)

        try:
            TwitchBot.Placeholder[parts[0]].process(parts, user, message)
        except Exception:
            return placeholder