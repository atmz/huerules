import simplejson as json
import requests
from time import sleep
from time import time
from datetime import datetime

host_id = "098f6bcd4621d373cade4e832627b4f6"
host = "http://192.168.1.102"
def _getState():
	state = {}
	r = requests.get("%s/api/%s/lights" % (host,host_id), timeout=3)
	lightsListResponseData = json.loads(r.content)
	for key, lamp in lightsListResponseData.iteritems():
		state[key]=lamp['state']
		state[key]['trigger'] = False
	return state

state = _getState()
states = []

def updateState():
	newState = _getState()
	changed = False
	for k,v in newState.iteritems():
		if state[k]['reachable']!=newState[k]['reachable']:
			changed = True
			newState[k]['trigger'] = True
		else:
			newState[k]['trigger'] = False
		state[k] = newState[k]
	return changed

def pushState():
	states.append(state)

def popState():
	state = states.pop()

def sendState(lid, state):
	r = requests.put("%s/api/%s/lights/%s/state" % (host, host_id, int(lid)), data=state)

def off(lid):
	sendState(lid, json.dumps({"on": False}))

def on(lid):
	sendState(lid, json.dumps({"on": True}))

def hueShift(lid, amount, transitiontime=4):
	sendState(lid, json.dumps({"hue_inc": amount, "transitiontime":transitiontime}))
def briShift(lid, amount, transitiontime=4):
	sendState(lid, json.dumps({"bri_inc": amount, "transitiontime":transitiontime}))
def satShift(lid, amount, transitiontime=4):
	sendState(lid, json.dumps({"sat_inc": amount, "transitiontime":transitiontime}))

def setAlert(lid, isLong=False):
	sendState(lid, json.dumps({"alert":'lselect' if isLong else 'select'}))
def clearAlert(lid):
	sendState(lid, json.dumps({"alert":'none'}))

def setHue(lid, hue, transitiontime=4):
	sendState(lid, json.dumps({"hue": hue, "transitiontime":transitiontime}))
def setBri(lid, bri, transitiontime=4):
	sendState(lid, json.dumps({"bri": bri, "transitiontime":transitiontime}))
def setSat(lid, sat, transitiontime=4):
	sendState(lid, json.dumps({"sat": sat, "transitiontime":transitiontime}))

def restoreState(lid, transitiontime=4):
	sendState(lid, json.dumps({
			'bri':state[lid]['bri'],
			'sat':state[lid]['sat'],
			'hue':state[lid]['hue'],
			}))

def restoreFullState(lid, transitiontime=4):
	if 'sat' in state[lid]:
		sendState(lid, json.dumps({
			'bri':state[lid]['bri'],
			'sat':state[lid]['sat'],
			'hue':state[lid]['hue'],
			'on':state[lid]['on'],
			}))
	else:
		sendState(lid, json.dumps({
			'bri':state[lid]['bri'],
			'on':state[lid]['on'],
			}))



def doForAll(fn, *args, **kwargs):
	for key in state.keys():
		fn(key, *args, **kwargs)

def alert(duration=15, hue=0):
	pushState()
	doForAll(on)
	doForAll(setHue,hue)
	doForAll(setAlert, True)
	sleep(duration)
	doForAll(clearAlert)
	popState()
	doForAll(restoreFullState)

def stepHueUntil(fn, timeInterval, hueInterval, lag=0):
	while not fn():
		for key in state.keys():
			hueShift(key, hueInterval, 0)
		updateState(state)
		sleep(timeInterval)
	if lag>0:
		for key in state.keys():
			hueShift(key, -(lag*hueInterval*(1/timeInterval)), 0)

def lampReachable(lid):
	def result():
		return state['4']['reachable']
	return result

	
