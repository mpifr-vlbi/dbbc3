:mod:`dbbc3` --- python control of the DBBC3 VLBI backend
=========================================================

Introduction
------------
The :mod:`dbbc3` package provides a python interface for monitoring and control of the DBBC3 VLBI backend.
It wraps most of the commands accepted by the DBBC3 control software and provides the 
contents of the command response in pythonic ways (dictionaries, lists etc.)


Installation
------------

Usage example
-------------

The following simple example will connect to the DBBC3 with host name "dbbc3" on the default port.
It will assume the DBBC3 is running the firmware and latest version control software of the DDC_V mode.
The dbbcif command is executed and the power of the first board is obtained and printed.

.. code-block:: python

    dbbc3 = DBBC3(host="dbbc3", mode="DDC_V")
    print (dbbc3.dbbcif(0))
    dbbc3.disconnect()

    Output:
    {'inputType': 2, 'attenuation': 24, 'mode': 'agc', 'count': 32095, 'target': 32000}


.. toctree::
   :hidden:

   source/introduction
   source/octd110
   source/octd120
   source/dsc110

