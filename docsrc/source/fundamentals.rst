Fundamentals
============

The :mod:`DBBC3` package provides a python interface to control the DBBC3 programatically by issuing commands and providing the command responses as python objects (e.g. dictionaries, lists, etc).
The core functionality is built around an instance of :py:class:`dbbc3.DBBC3`.

.. code-block:: python

  from dbbc3.DBBC3 import DBBC3  

  dbbc3 = DBBC3 ( host = 'dbbc3hostname')
                
Upon initialization a connection is established to the DBBC3, the currently running mode and version is determined and the corresponding command set is attached to the DBBC3 instance. For example to obtain the
current state of the first GCoMo IF module the following command can be issued:

.. code-block:: python

   dbbc.dbbcif('A')

Finally the connection should be released:

.. code-block:: python

   dbbc3.disconnect()

Note that the  control software running on the DBBC3 computer accepts a single client connection only. Make sure that all other client connections, e.g. by the dbbc3 client software, the VLBI Field System etc. have been closed prior to starting your script.

Command structure
-----------------

The dbbc3 commands provided by the python module tyically follow the nameing scheme of the original DBBC3 commands accepted by the DBBC3 control software.
