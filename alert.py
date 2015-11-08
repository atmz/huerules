import redis
import sys

r = redis.StrictRedis(host='localhost', port=6379, db=0)

for line in sys.stdin:
	if 'PagerDuty' in line:
			r.publish('hue','{"transitions":{"hue":0,"sat":220,"bri":255, "on":true}, "type":"alert", "duration":10}')
		break
