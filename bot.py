import socket
import atexit
import os

TWITCH_HOST = 'irc.chat.twitch.tv'
TWITCH_PORT = 6667

class DiceBot(object):
    def __init__(self):
        self.nickname = 'DiceBot'
        self.password = os.environ['TWITCH_OAUTH']
        self.channel = os.environ['TWITCH_USER']
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.connect((TWITCH_HOST, TWITCH_PORT))
        self.irc.settimeout(3)

        self.write_to_system('PASS %s' % self.password)
        self.write_to_system('NICK %s' % self.nickname)
        self.write_to_system('USER %s 0 * %s' % (self.nickname, self.nickname))
        self.write_to_system('JOIN #%s' % self.channel)
    
    def write_to_system(self, message):
        print(message)
        self.irc.send(message + "\n")
    
    def write_to_chat(self, message):
        self.write_to_system('PRIVMSG #%s :%s' % (self.channel, message))
    
    def quit(self):
        self.write_to_chat('Bye!')
        self.write_to_system('PART #%s' % self.channel)
        self.write_to_system('QUIT')

dicebot = DiceBot()
# atexit.register(dicebot.quit)
print(dicebot.irc.recv(2048))
# dicebot.write_to_chat("hello world")

