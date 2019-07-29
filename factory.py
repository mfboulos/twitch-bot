from twisted.internet import protocol, reactor
from collections import defaultdict
from importlib import reload
from bot import DiceBot
from enum import Enum

import typing
import time
import bot

TWITCH_HOST = 'irc.chat.twitch.tv'
TWITCH_PORT = 6667

class BotFactory(protocol.ClientFactory):
    MAX_WAIT_TIME = 512

    def __init__(self, bot_class):
        self.protocol = bot.CustomBotProtocol
        self.bot_class = bot_class
        self.connection = None

        self.tags = defaultdict(dict)
        self.activity = dict()
        self.wait_time = 1

    def clientConnectionLost(self, connector, reason):
        # TODO: log reason
        print('REASON:\n', reason)
        self.protocol = reload(bot).CustomBotProtocol
        connector.connect()
    
    def clientConnectionFailed(self, connector, reason):
        # TODO: log reason
        print(44)
        time.sleep(self.wait_time)
        self.wait_time = min(self.MAX_WAIT_TIME, self.wait_time * 2)
        connector.connect()
    
    def buildProtocol(self, addr):
        self.connection = self.protocol(self.bot_class, factory=self)
        return self.connection

if __name__ == "__main__":
    reactor.connectTCP(TWITCH_HOST, TWITCH_PORT, BotFactory(DiceBot))
    reactor.run()