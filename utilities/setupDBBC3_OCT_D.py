#!/usr/bin/env python

from dbbc3.DBBC3 import DBBC3
from dbbc3.DBBC3Config import DBBC3Config
from dbbc3.DBBC3Validation import DBBC3Validation
import re
import sys
import numpy as np

from time import sleep

if __name__ == "__main__":

	#try:
                config = DBBC3Config()

                config.numCoreBoards = 4
                config.host="192.168.0.60"

                dbbc3 = DBBC3(config, mode="OCT_D", version=110)
                
		dbbc3.connect()


		print "=== Disabling calibration loop"
		dbbc3.disableloop()
	
                val = DBBC3Validation(dbbc3, ignoreErrors=True)
		val.validateSynthesizerLock(0)
		val.validateSynthesizerLock(1)
		val.validateSynthesizerLock(2)
		val.validateSynthesizerLock(3)
 
		val.validateSynthesizerFreq(0)
		val.validateSynthesizerFreq(1)
		val.validateSynthesizerFreq(2)
		val.validateSynthesizerFreq(3)

		val.validateIFLevel('a')
		val.validateIFLevel('b')
		val.validateIFLevel('c')
		val.validateIFLevel('d')

		val.validateSamplerPhases()

 		val.validateSamplerPower(0)
 		val.validateSamplerPower(1)
		val.validateSamplerPower('C')
		val.validateSamplerPower('D')

 		val.validateSamplerOffsets(1)
 		val.validateSamplerOffsets(2)
		val.validateSamplerOffsets('C')
		val.validateSamplerOffsets('D')

		
		# load tap filters (extra script)
		response = raw_input("Do you want to set the tap filters now? [y/n]")
		if response == "y":
 			print "=== Loading tap filters for board A"
 			dbbc3.tap(1,"2000-4000_floating.flt")
 			dbbc3.tap2(1,"0-2000_floating.flt")
 			print "=== Loading tap filters for board B"
 			dbbc3.tap(2,"2000-4000_floating.flt")
 			dbbc3.tap2(2,"0-2000_floating.flt")
			print "=== Loading tap filters for board C"
			dbbc3.tap(2,"2000-4000_floating.flt")
			dbbc3.tap2(2,"0-2000_floating.flt")
			print "=== Loading tap filters for board D"
			dbbc3.tap(3,"2000-4000_floating.flt")
			dbbc3.tap2(3,"0-2000_floating.flt")
		else:	
			sys.exit(0)

		print "=== Setting up calibration loop"
		dbbc3.enablecal()
		print "=== Enabling calibration loop"
		dbbc3.enableloop()

		print "=== Waiting for 1 minute to allow adjusting the power levels"
		sleep(60)
		
		print "=== Now re-checking the bit statistics (should be proper 2-bit)"
 		val.validateSamplerOffsets(0)
 		val.validateSamplerOffsets(1)
		val.validateSamplerOffsets(2)
		val.validateSamplerOffsets(3)

		print "=== Setting up calibration loop"
		dbbc3.enablecal()
		print "=== Enabling calibration loop"
		dbbc3.enableloop()
		
		dbbc3.disconnect()
		print "=== Done"

 #	except Exception as e:
 #		print e.message
 #		dbbc3.disconnect()
		

	
