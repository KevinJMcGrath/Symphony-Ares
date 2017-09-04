import redis
from rq import Worker, Queue, Connection

import modules.botconfig as config

listen = ['high', 'default', 'low']

conn = redis.StrictRedis(
    host=config.RedisHost,
    port=config.RedisPort,
    password=config.RedisPassword)

conn.ping()

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
