from bot_config import TwitchBotConfig, DiceBotConfig
from twisted.words.protocols.irc import IRCClient
from twisted.internet import reactor

import requests
import typing
import socket
import atexit
import json
import os

USERLIST_API = 'http://tmi.twitch.tv/group/user/%s/chatters'

class BotProtocol(IRCClient, object):
    nickname = os.environ['TWITCH_USER']
    password = os.environ['TWITCH_OAUTH']

    def __init__(self, factory=None):
        self.factory = factory
        self.bots = [DiceBot()] # TODO: set up a db and query for all bots

    def signedOn(self):
        self.factory.wait_time = 1

        self.activity = self.factory.activity
        self.tags = self.factory.tags

class TwitchBot(object):
    def __init__(self,
                 config: TwitchBotConfig,
                 protocol: BotProtocol):
        self.channel = config.channel
        self.password = config.password
        self.nickname = config.nickname
        self.ignore_patterns = config.ignore_patterns
        
        self.protocol = protocol

        user_data = requests.get(USERLIST_API % self.channel[1:]).json()
        chatters = user_data['chatters']
        self.users = set(sum(chatters.values(), []))
        self.mods = set(chatters['moderators'])
        self.subs = set()

    def write(self, message):
        self.protocol.say(self.channel, message)

class DiceBot(TwitchBot):
    def __init__(self,
                 config: DiceBotConfig,
                 protocol: BotProtocol):
        super().__init__(config, protocol)