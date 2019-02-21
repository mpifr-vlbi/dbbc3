#!/usr/bin/env python

from dbbc3.DBBC3 import DBBC3
from dbbc3.DBBC3Config import DBBC3Config
from dbbc3.DBBC3Validation import DBBC3Validation
import re
import sys
import numpy as np

from time import sleep

if __name__ == "__main__":

	try:

                config = DBBC3Config()

                config.numCoreBoards = 5
                config.host="134.104.30.208"

                dbbc3 = DBBC3(config, mode="DDC_V", version=124)
                val = DBBC3Validation(dbbc3, ignoreErrors=True)
                
		dbbc3.connect()
		
		val.validatePPS()

		for board in range(0, config.numCoreBoards):
			val.validateTimesync(board)
			val.validateSynthesizerLock(board)
			val.validateSynthesizerFreq(board)
			val.validateIFLevel(board)
 			val.validateSamplerPower(board)
 			val.validateSamplerOffsets(board)
		

		dbbc3.disconnect()
		print "=== Done"

 	except Exception as e:
 		print e.message
 		dbbc3.disconnect()
		

	
