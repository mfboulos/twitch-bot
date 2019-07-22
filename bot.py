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

    def quit(self):
        self.close_commands()
        reactor.stop()

class DiceBot(object):
    def __init__(self):
        self.nickname = 'DiceBot' #TODO: register a new Twitch account for this
        self.password = os.environ['TWITCH_OAUTH']
        self.channel = os.environ['TWITCH_USER']
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.connect((TWITCH_HOST, TWITCH_PORT))
        self.irc.settimeout(3)

        self.__write_to_system('PASS %s' % self.password)
        self.__write_to_system('NICK %s' % self.nickname)
        self.__write_to_system('JOIN #%s' % self.channel)
    
    def __write_to_system(self, message):
        self.irc.send(message + "\r\n")
    
    def write_to_chat(self, message):
        self.__write_to_system('PRIVMSG #%s :%s' % (self.channel, message))
    
    def quit(self):
        self.write_to_chat('Bye!')
        self.__write_to_system('PART #%s' % self.channel)
        self.__write_to_system('QUIT')

dicebot = DiceBot()
# atexit.register(dicebot.quit)
print(dicebot.irc.recv(2048))
# dicebot.write_to_chat("hello world")

