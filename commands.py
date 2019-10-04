# from twisted.words.protocols.irc import IRCClient

from neomodel import StructuredNode, StringProperty, RelationshipFrom
#, IntegerProperty, DateTimeProperty, RelationshipTo
from neomodel.cardinality import One, OneOrMore

# from datetime import datetime, timedelta
# from enum import Enum, auto

from relationships import CommandUseRel

# import random
# import re

class Command(StructuredNode):
    response = StringProperty(required=True)
    bots = RelationshipFrom('bot.TwitchBot', 'CAN_USE', cardinality=OneOrMore,
                           model=CommandUseRel)
    owner = RelationshipFrom('bot.TwitchBot', 'OWNS', cardinality=One)

    def __init__(self, response, *args, **kwargs):
        kwargs['response'] = response

        super().__init__(*args, **kwargs)

# We'll probably integrate this into CommandUseRel
# class TimedRule(Rule, StructuredNode):
#     response = StringProperty()
#     min_messages = IntegerProperty(default=5)
#     num_messages = IntegerProperty(default=0)
#     cooldown = IntegerProperty(default=300)
#     last_called = DateTimeProperty(default_now=datetime.now)
#     bots = RelationshipFrom('bot.TwitchBot', 'CAN_USE', cardinality=OneOrMore,
#                            model=CommandUseRel)
#     owner = RelationshipFrom('bot.TwitchBot', 'OWNS', cardinality=One)

#     def __init__(self, response=None, *args, **kwargs):
#         kwargs['response'] = response
#         super().__init__(*args, **kwargs)
    
#     @property
#     def _ready(self):
#         """
#         Determines whether this rule is ready to be executed again.
        
#         :return:
#         :rtype: bool
#         """

#         message_check = self.num_messages >= self.min_messages
#         time_check = datetime.now() - self.last_called > timedelta(seconds=self.intecooldownrval)
#         return message_check and time_check
    
#     # TODO: rewrite to take either bot or write function
#     def run(self, user, message):
#         """
#         Makes the bot write this command's message if the command is ready
#         """

#         self.num_messages += 1
#         if self._ready:
#             self.num_messages = 0

# I'm just gonna keep this around til I make a roll command with the current framework

# class RollCommand(ExecutedCommand):
#     def __init__(self, bot: IRCClient):
#         super().__init__(bot, '!roll')
    
#     def _parse_message(self, message):
#         exec_token, args = super()._parse_message(message)
#         match = re.search('(\d+)d(\d+)', args[0]) if args else None
#         if match:
#             return exec_token, int(match.group(1)), int(match.group(2))
#         else:
#             return exec_token, None, None

#     def _match(self, message):
#         return all(self._parse_message(message))
    
#     def run(self, user, channel, message):
#         if self._match(message):
#             exec_token, amount, dice_faces = self._parse_message(message)
#             amount = max(1, min(100, amount))
#             dice_faces = max(1, min(100, dice_faces))

#             total = 0
#             for _ in range(amount):
#                 total += random.randint(1, dice_faces)
            
#             response = '/me @%s rolling %dd%d: %d' % (user, amount, dice_faces, total)
#             if total is amount:
#                 response += ' LUL'
#             elif total is amount * dice_faces:
#                 response += ' PogChamp'
#             self._bot.say(channel, response)