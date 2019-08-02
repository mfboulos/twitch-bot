from neomodel import StructuredRel, BooleanProperty, StringProperty

class CommandUseRel(StructuredRel):
    name = StringProperty(required=True, db_property='name')
    enabled = BooleanProperty(default=True)

    def __init__(self, name, *args, **kwargs):
        kwargs['name'] = name
        super().__init__(*args, **kwargs)