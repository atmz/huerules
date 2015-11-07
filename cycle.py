from huelib import *
import sys
import select

print("Host is %s" % host)
print("Host ID is %s" % host_id)
doForAll(on)
doForAll(setHue, 42000)
doForAll(setBri, 255)
doForAll(setSat, 255)
while True:
	sleep(.4)
	doForAll(hueShift,1000,4)
	if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
			line = raw_input()
			break
doForAll(setBri, 0)
while True:
	sleep(.4)
	doForAll(briShift,40,4)
	if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
			line = raw_input()
			break

doForAll(setSat, 0)
while True:
	sleep(.4)
	doForAll(satShift,40,4)
	if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
			line = raw_input()
			break
	
