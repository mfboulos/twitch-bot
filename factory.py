import time
from importlib import reload

from twisted.internet import protocol

import bot

BOT_NAME = 'SolBot'

class BotFactory(protocol.ClientFactory):
    MAX_WAIT_TIME = 512

    def __init__(self):
        self.protocol = bot.BotProtocol
        self.connection = None
        self.wait_time = 1

    def clientConnectionLost(self, connector, reason):
        # TODO: log reason
        self.protocol = reload(bot).BotProtocol
        connector.connect()
    
    def clientConnectionFailed(self, connector, reason):
        # TODO: log reason
        time.sleep(self.wait_time)
        self.wait_time = min(self.MAX_WAIT_TIME, self.wait_time * 2)
        connector.connect()
    
    def buildProtocol(self, addr):
        self.connection = self.protocol.nodes.get_or_none(nickname=BOT_NAME)
        if not self.connection:
            self.connection = self.protocol(BOT_NAME).save()
        self.connection.factory = self
        return self.connection