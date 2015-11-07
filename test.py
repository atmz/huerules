from huelib import *

print("Host is %s" % host)
print("Host ID is %s" % host_id)
doForAll(on)
doForAll(setHue, 42000)
doForAll(setBri, 255)
doForAll(setSat, 255)
while True:
	sleep(0.1)
	stateChanged = updateState()
	if state['4']['trigger'] and not state['4']['reachable']:
		stepHueUntil(lampReachable('4'),1,7500,3.5)
	if state['1']['trigger'] and not state['1']['reachable']:
		print(state['1'])
		doForAll(off)
	if state['1']['trigger'] and state['1']['reachable']:
		print(state['1'])
		doForAll(on)
		restoreState('1')


	
