Fundamentals
============

The :mod:DBBC3 package provides a python interface to control the DBBC3 programatically by issuing commands and providing the command responses as python objects (e.g. dictionaries, lists, etc).
The cre functionality is built around an instance of DBBC3.DBBC3.
:py:class:`DBBC3.DBBC3`

from DBBC3 import DBBC3

dbbc3 = DBBC3 ( host = 'dbbc3hostname',
              port = 
