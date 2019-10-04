from neomodel import StructuredNode, StringProperty, RelationshipFrom

from relationships import BotAccumRel

class Accumulator(StructuredNode):
    emote = StringProperty(unique_index=True, required=True)
    bots = RelationshipFrom('bot.TwitchBot', 'ACCUMULATED', model=BotAccumRel)

    def __init__(self, emote, *args, **kwargs):
        kwargs['emote'] = emote

        super().__init__(*args, **kwargs)