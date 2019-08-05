import random

class PlaceholderOp(object):
    def process(self, parts, user, message):
        """
        Processes a command placeholder
        
        :param parts: command placeholder parts (ex: `{arg|1}` => `[args, 1]`)
        :type parts: list
        :param user: username invoking the command
        :type user: str
        :param message: full message of the user invoking the command
        :type message: str
        :raises NotImplementedError:
        """
        raise NotImplementedError

class UserOp(PlaceholderOp):
    """
    Placeholder op for `{user}`

    Replaces it with the name of the user invoking the command.
    """
    def process(self, parts, user, message):
        return user

class ArgsOp(PlaceholderOp):
    """
    Placeholder op for `{args|x}`.

    Replaces it with the argument from the invoking message's tokens indicated
    by the index `int(x)`.
    """
    def process(self, parts, user, message):
        return message.split()[int(parts[1])]

class RandomOp(PlaceholderOp):
    """
    Placeholder op for `{random|item1|item2|...}`.

    Replaces it with a (psuedo-)randomly chosen item from `[item1, item2, ...]`.
    """
    def process(self, parts, user, message):
        return random.choice(parts[1:])