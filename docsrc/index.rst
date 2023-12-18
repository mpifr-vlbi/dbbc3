:mod:`dbbc3` --- python control of the DBBC3 VLBI backend
=========================================================

Introduction
------------
The :mod:`dbbc3` package provides a python interface for software control of the DBBC3 VLBI backend.
It wraps most of the commands accepted by the DBBC3 control software and provides the 
contents of the command response in pythonic ways (dictionaries, lists etc.). For a reference of
the available commands consult the CommandSet section.

In addition the package provides a number of utilities for higher level functionality like pre-observation
validation of the DBBC3 state or  graphical monitoring of the DBBC3 parameters during the observations.

Usage example
-------------

The following simple example will connect to the DBBC3 with host name "dbbc3" on the default port.
After a succefull connection the currently running DBBC3 software mode and version is automatically
determined and the corresponding command set is enabled.
The dbbcif command is executed and the power of the first board is obtained in form of a dictionary and is printed.

.. code-block:: python

    
    dbbc3 = DBBC3(host="dbbc3")
    print (dbbc3.dbbcif(0))
    dbbc3.disconnect()

    Output:
    {'inputType': 2, 'attenuation': 24, 'mode': 'agc', 'count': 32095, 'target': 32000}

More detailed instructions for using the python package can be found in the usage section. 

Installation
-------------

Clone the code from github:

``git clone https://github.com/mpifr-vlbi/dbbc3.git``

Do a system wide installation (might require root priviliges):

``cd dbbc3/lib
python setup.py install``

Alternatively you can do a local installation (current user only):

``python setup.py install --user``

Note: This will only install the dbbc3 package. The standalone utilities and scripts located in the utilities subdirectory must be
manually copied to the target location by the user.



.. toctree::
   :maxdepth: 1

   source/installation    
   source/utilities
   source/commandsets

