import os

class Neo4JConfig:
    user = os.environ['NEO4J_USER']
    password = os.environ['NEO4J_PASS']
    host = os.environ['NEO4J_HOST']
    port = os.environ['NEO4J_PORT']