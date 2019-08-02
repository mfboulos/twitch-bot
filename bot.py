from neomodel import StructuredNode, StringProperty, ArrayProperty, RelationshipTo, RelationshipFrom
from neomodel.cardinality import One

from twisted.words.protocols.irc import IRCClient
from twisted.internet import reactor

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
    
    @classmethod
    def channel_no_prefix(self, channel):
        return channel[1:] if channel[0] in '&#!+' else channel

    @classmethod
    def channel_with_prefix(self, channel):
        return '#' + channel_no_prefix(channel)

class TwitchBot(StructuredNode):
    channel = StringProperty(unique_index=True, required=True)
    ignore = ArrayProperty(base_property=StringProperty())
    usable_commands = RelationshipTo('Command', 'CAN_USE', model=CommandUseRel)
    owned_commands = RelationshipTo('Command', 'OWNS')
    protocol = RelationshipFrom('BotProtocol', 'PROVIDES_IRC_FOR', cardinality=One)

    def __init__(self,
                 channel,
                 ignore=['nightbot', 'moobot', 'streamelements', '.+bot']):
        kwargs['channel'] = BotProtocol.channel_no_prefix(channel)
        kwargs['ignore'] = ignore

        user_data = requests.get(USERLIST_API.format(self.channel)).json()
        chatters = user_data['chatters']
        self.users = set(sum(chatters.values(), []))
        self.mods = set(chatters['moderators'])
        self.subs = set()

        super().__init__(*args, **kwargs)
    
    @property
    def _max_lines(self):
        return 5
    
    def write(self, message):
        for line in message.split('\n')[:5]:
            self.protocol.single().say(self.channel, line)