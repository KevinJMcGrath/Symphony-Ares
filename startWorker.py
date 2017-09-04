import os

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

conn = redis.StrictRedis(
	host='localhost',
	port=6379,
	password='suzumebachi')

conn.ping()

if __name__ == '__main__':
	with Connection(conn):
		worker = Worker(map(Queue, listen))
		worker.work()
