from huelib import *
import sys

for line in sys.stdin:
	if 'PagerDuty' in line:
		alert(10)
		doForAll(on)
		break
