import redis
from huelib import *

r = redis.StrictRedis(host='localhost', port=6379, db=0)
p = r.pubsub()
p.subscribe('hue')
state = State(host_id, host)
while True:
	state.updateState()
	message = p.get_message()
	if message and message['type']=='message':
		print message
		action = json.loads(message['data'])
		if('alert' == action.get('type','')):
			state.doAlert(action)
		else:
			state.doTransition(action['lids'], action.get('duration',4), action['transitions'])