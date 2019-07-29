import os

class TwitchBotConfig(object):
    """
    Configuration required to initialize a `bot.TwitchBot` instance.

    Defaults require the environment variables as they are named.
    """

    def __init__(self,
                 channel=os.environ['TWITCH_USER'],
                 password=os.environ['TWITCH_OAUTH'],
                 nickname=None,
                 ignore_patterns=['nightbot', 'moobot', '.+_bot'],
                 hello=None,
                 goodbye='Goodbye!'):
        self.channel = channel[1:] if channel.startswith('#') else channel
        self.password = password
        self.nickname = nickname if nickname else channel + '_bot'
        self.ignore_patterns = ignore_patterns
        self.hello = hello if hello else 'Hello @%s! :)' % self.channel
        self.goodbye = goodbye

class DiceBotConfig(TwitchBotConfig):
    def __init__(self,
                 channel = os.environ['TWITCH_USER'],
                 password = os.environ['TWITCH_OAUTH'],
                 ignore_patterns = ['nightbot', 'moobot', '.+_bot']):
        self.channel = channel[1:] if channel.startswith('#') else channel
        super().__init__(channel, password, 'DiceBot', ignore_patterns,
                         'Hey @%s, ready to roll?' % self.channel)