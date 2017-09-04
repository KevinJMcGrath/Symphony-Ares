from redis import Redis
from rq import Queue

redis_conn = Redis(host='localhost', port=6379, password='suzumebachi')

commandQueue = Queue('default', connection=redis_conn)

jobQueue = []


def AsyncCommand(func, messageDetail):
    job = commandQueue.enqueue(func, messageDetail)
    jobQueue.append(job)
