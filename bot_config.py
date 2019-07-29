import os

class TwitchBotConfig(object):
    """
    Configuration required to initialize a `bot.TwitchBot` instance.

    Defaults require the environment variables as they are named.
    """

    def __init__(self,
                 channel = '#' + os.environ['TWITCH_USER'],
                 password = os.environ['TWITCH_OAUTH'],
                 nickname = channel + '_bot',
                 ignore_patterns = ['nightbot', 'moobot', '.+_bot']):
        self.channel = channel
        self.password = password
        self.nickname = nickname
        self.ignore_patterns = ignore_patterns

class DiceBotConfig(TwitchBotConfig):
    def __init__(self,
                 channel = '#' + os.environ['TWITCH_USER'],
                 password = os.environ['TWITCH_OAUTH'],
                 ignore_patterns = ['nightbot', 'moobot', '.+_bot'])):
        super().__init__(channel, password, 'DiceBot', ignore_patterns)