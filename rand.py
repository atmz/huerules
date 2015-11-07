from huelib import *
import random
import sys
import select

print("Host is %s" % host)
print("Host ID is %s" % host_id)
doForAll(on)
doForAll(setHue, 42000)
doForAll(setBri, 255)
doForAll(setSat, 255)
while True:
	sleep(10)
	doForAll(setHue,random.randint(0,65550),100)
	if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
			line = raw_input()
			break
