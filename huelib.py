import simplejson as json
import requests
from time import sleep
from time import time
from datetime import datetime

host_id = "098f6bcd4621d373cade4e832627b4f6"
host = "http://192.168.1.102"
USER_PRIORITY = 5
USER_DURATION = 600
DEFAULT_PRIORITY=10
TRANSITION_DELAY_BUFFER=10
PROPS=['on','bri','hue','sat']

class State:
	def __init__(self, host_id, host):
		self._api_path = "%s/api/%s/lights" % (host,host_id)
		self._stack = []
		self._currentTransitions = {}
		self._lastChanged = {}
		self._updateTimes = []
		self._state = self._getState()

	def _getState(self):
		self._updateTimes.append(time())
		r = requests.get(self._api_path, timeout=3)
		lightsListResponseData = json.loads(r.content)
		state = {}
		for key, lamp in lightsListResponseData.iteritems():
			state[key]=lamp['state']
			state[key]['trigger'] = False
			state[key]['changed'] = False
			state[key]['id'] = key
			if key not in self._currentTransitions.keys():
				self._currentTransitions[key]={}
				self._lastChanged[key]={}
		return state

	def handleChange(self, light):
		lid = light['id']
		transition =  self._currentTransitions[lid]
		unexpected = light['trigger'] or not transition
		if transition and not unexpected:
			previous = self._state[lid]
			# if non-transition bits of the lights state have changed, a user action has happened
			for prop in PROPS:
				if prop not in transition and light.get(prop,None)!=previous.get(prop,None):
					if 'ct' not in transition or prop=='bri':
						unexpected = True

		now = time()
		if unexpected:
			#all triggers are from user event 
			print 'User changed light %s' % lid
			self._lastChanged[light['id']]['source'] = 'user'
			self._lastChanged[light['id']]['priority'] = USER_PRIORITY
			self._lastChanged[light['id']]['until'] =  now + USER_DURATION
			self._currentTransitions[lid]['end_time'] = now
		elif self._currentTransitions[lid]['end_time']>now:
			print 'Transition running on light %s' % lid
			self._lastChanged[light['id']]['source'] = 'user'
			self._lastChanged[light['id']]['priority'] = self._currentTransitions[lid]['priority']
			self._lastChanged[light['id']]['until'] =  self._currentTransitions[lid]['end_time']
		else:
			print "Light %s changed, but after the last transition's end time" % lid
			self._currentTransitions[lid] = {}

	def updateState(self):
		self.updateTransitions()
		newState = self._getState()
		for k,v in newState.iteritems():
			if self._state[k]['reachable']!=newState[k]['reachable']:
				newState[k]['trigger'] = True
				newState[k]['changed'] = True
				self.handleChange(newState[k])
			elif ([newState[k].get(p,None) for p in PROPS] != [self._state[k].get(p,None) for p in PROPS]):
				newState[k]['changed'] = True
				self.handleChange(newState[k])
			self._state[k] = newState[k]
	
	def updateTransitions(self):
		earliest_possible_change_time = self._updateTimes[-1] if len(self._updateTimes)>0 else 0
		for k,t in self._currentTransitions.iteritems():
			self._currentTransitions[k] = t if (t and t['end_time']>(earliest_possible_change_time-TRANSITION_DELAY_BUFFER)) else {}
	
	def _canPerformTransition(self, lid, priority):
		if self._currentTransitions[lid] and self._currentTransitions[lid]['priority']<priority:
			return False
		if self._lastChanged[lid].get('until',0)>time() and self._lastChanged[lid]['priority']<priority:
			return False
		return True
		
	
	def doTransition(self, lids, duration, transitions):
		transitions['priority'] = transitions.get('priority',DEFAULT_PRIORITY)
		transitions['transitiontime'] = int(duration*10)
		priority = transitions['priority'] 
		for lid in lids:
			if self._canPerformTransition(lid, priority):
				r = requests.put("%s/%s/state" % (self._api_path, int(lid)), data=json.dumps(transitions))
				transitions['end_time'] =  transitions.get('end_time', time()+duration)
				self._currentTransitions[lid]=transitions
			else:
				print 'Cannot perform transaction of priority %d on light %s at this time' % (priority, lid)


	def restoreFullState(self, lids, duration=0):
		for lid in lids:
			light = self._state[lid]
			if 'sat' in light:
				self.doTransition(
					[lid], 
					duration,
					{
					'bri':light['bri'],
					'sat':light['sat'],
					'hue':light['hue'],
					'on':light['on'],
					})
			else:
				self.doTransition(
					[lid],
					duration,
					{
					'bri':light['bri'],
					'on':light['on'],
					})

	def pushState(self):
		self._stack.append(self._state.copy())
	def popState(self):
		self._state=self._stack.pop()


	def doAlert(self, alert):
		lids = alert.get('lids', self._state.keys())
		transitions = alert.get('transitions',{})
		self.pushState()
		transitions['alert']='lselect'
		self.doTransition(lids, 0, transitions)
		sleep(alert.get('duration',2))
		self.doTransition(lids,0, {"alert":'none'})
		self.popState()
		self.restoreFullState(lids)


