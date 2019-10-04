from neomodel import install_all_labels, config
from twisted.internet import reactor
from db_config import Neo4JConfig
from factory import BotFactory

TWITCH_HOST = 'irc.chat.twitch.tv'
TWITCH_PORT = 6667

if __name__ == "__main__":
    config.DATABASE_URL = "bolt://{user}:{password}@{host}:{port}".format(
        user=Neo4JConfig.user,
        password=Neo4JConfig.password,
        host=Neo4JConfig.host,
        port=Neo4JConfig.port
    )
    install_all_labels()
    reactor.connectTCP(TWITCH_HOST, TWITCH_PORT, BotFactory())
    reactor.run()