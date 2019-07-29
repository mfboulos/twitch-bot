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

class BotAlreadyJoinedException(Exception):
    """
    Thrown when there is already a bot in a particular room.
    """
    pass

# This class is gonna need a lot of work in the long run
class CustomBotProtocol(IRCClient, object):
    nickname = os.environ['TWITCH_USER']
    password = os.environ['TWITCH_OAUTH']

    def __init__(self,
                 bot_class,
                 factory=None):
        self.factory = factory
        self.bots = dict() # channel to bot key value pair

    def signedOn(self):
        self.factory.wait_time = 1

        self.activity = self.factory.activity
        self.tags = self.factory.tags

        bots = [DiceBot(DiceBotConfig(), self)] # TODO: set up a db and query for all custom bots using bot_class

        for bot in bots:
            self.join(bot)
    
    def join(self, bot):
        if bot.channel in self.bots:
            raise BotAlreadyJoinedException
        
        super().join(bot.channel)

    def joined(self, channel):
        self.say(channel, 'Hello @%s!' % channel)
        bots[bot.channel] = bot

    def privmsg(self, user, channel, message):
        self.say(channel, 'Nice!')
        self.leave(channel)
    
    def left(self, channel):
        self.say(channel, 'Bye!')
        bots.pop(channel)

class TwitchBot(object):
    def __init__(self,
                 config: TwitchBotConfig,
                 protocol: CustomBotProtocol):
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
                 protocol: CustomBotProtocol):
        super().__init__(config, protocol)