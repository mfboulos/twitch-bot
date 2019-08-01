from twisted.internet import protocol, reactor
from collections import defaultdict
from importlib import reload
from bot import DiceBot
from enum import Enum

import typing
import time
import bot

class BotFactory(protocol.ClientFactory):
    MAX_WAIT_TIME = 512

    def __init__(self):
        self.protocol = bot.DiceBot
        self.connection = None

        self.tags = defaultdict(dict)
        self.activity = dict()
        self.wait_time = 1

    def clientConnectionLost(self, connector, reason):
        # TODO: log reason
        self.protocol = reload(bot).DiceBot
        connector.connect()
    
    def clientConnectionFailed(self, connector, reason):
        # TODO: log reason
        time.sleep(self.wait_time)
        self.wait_time = min(self.MAX_WAIT_TIME, self.wait_time * 2)
        connector.connect()
    
    def buildProtocol(self, addr):
        self.connection = self.protocol(factory=self)
        return self.connection