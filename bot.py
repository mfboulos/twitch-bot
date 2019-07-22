import socket
import os

TWITCH_HOST = "irc.twitch.tv"
TWITCH_PORT = 6667

class DiceBot(object):
    def __init__(self):
        self.nickname = "DiceBot"
        self.password = os.environ['TWITCH_OAUTH']
        self.channel = os.environ['TWITCH_USER']
        self.socket = socket.create_connection((TWITCH_HOST, TWITCH_PORT))

        self.write_to_system("PASS %s" % self.password)
        self.write_to_system("NICK %s" % self.nickname)
        self.write_to_system("USER %s 0 * %s" % (self.password, self.password))
        self.write_to_system("JOIN #%s" % self.channel)
    
    def write_to_system(self, message):
        self.socket.sendall(message)

dicebot = DiceBot()