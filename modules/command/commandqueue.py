from redis import Redis
from rq import Queue

import modules.botconfig as config

redis_conn = Redis(host=config.RedisHost, port=config.RedisPort, password=config.RedisPassword)

commandQueue = Queue('default', connection=redis_conn)

jobQueue = []


def AsyncCommand(func, messageDetail):
    job = commandQueue.enqueue(func, messageDetail)
    jobQueue.append(job)
