from twisted.words.protocols import irc
from twisted.internet import reactor
import requests
import socket
import atexit
import json
import os

TWITCH_HOST = 'irc.chat.twitch.tv'
TWITCH_PORT = 6667
USERLIST_API = 'http://tmi.twitch.tv/group/user/%s/chatters'

class TwitchBot(irc.IRCClient, object):
    def __init__(self,
                 channel,
                 password,
                 nickname=os.environ['TWITCH_USER']+'_bot',
                 admins=[],
                 ignores=['nightbot'],
                 command_classes=[]):
        self.channel = channel
        self.password = password
        self.nickname = nickname
        self.admins = admins
        self.ignores = ignores
        self.command_classes = command_classes
        super().__init__()
    
    def signedOn(self):
        self.factory.wait_time = 1

        user_data = requests.get(USERLIST_API % self.channel[1:]).json()
        chatters = user_data['chatters']
        self.users = set(sum(chatters.values(), []))
        self.mods = set(chatters['moderators'])
        self.subs = set()
        
        self.reload_commands()

        self.activity = self.factory.activity
        self.tags = self.factory.tags

    def write(self, message):
        self.msg(self.channel, message)
    
    def reload_commands(self):
        self.close_commands()
        #TODO: reload(commands)
        self.commands = [command(self) for command in self.command_classes]

    def close_commands(self):
        for command in self.commands:
            command.close(self)

    def terminate(self):
        self.close_commands()
        reactor.stop()

class DiceBot(TwitchBot):
    def __init__(self,
                 channel,
                 password,
                 nickname=os.environ['TWITCH_USER']+'_dicebot',
                 admins=[],
                 ignores=['nightbot'],
                 command_classes=[]):
        dice_command_classes = [] # TODO: dice command classes
        super().__init__(channel,
                         password,
                         nickname=nickname,
                         admins=admins,
                         ignores=ignores,
                         command_classes=list(set(command_classes + dice_command_classes)))