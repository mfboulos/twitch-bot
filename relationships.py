from neomodel import StructuredRel, BooleanProperty, StringProperty, IntegerProperty

from enum import Enum, auto

class Permission(IntEnum):
    USER = auto()
    SUB = auto()
    MOD = auto()
    ADMIN = auto()

class CommandUseRel(StructuredRel):
    name = StringProperty(required=True)
    permission = IntegerProperty(required=True)
    enabled = BooleanProperty(default=True)

    def __init__(self, name, p, *args, **kwargs):
        kwargs['name'] = name
        kwargs['permission'] = Permission(p) is type(p) is int else p

        super().__init__(*args, **kwargs)

class ProtocolBotRel(StructuredRel):
    channel = StringProperty(required=True)

    def __init__(self, channel, *args, **kwargs):
        kwargs['channel'] = channel
        
        super().__init__(*args, **kwargs)