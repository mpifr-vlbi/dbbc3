============
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

-----------------
Command structure
-----------------

The dbbc3 commands provided by the python module tyically follow the nameing scheme of the original DBBC3 commands accepted by the DBBC3 control software::

  python method = prefix_dbbc3CommandName

Possible prefixes are:

* no prefix: for general DBBC3 commands e.g. time()
* adb3l:  for adb3l commands e.g. adb3l_reseth()
* core3h: for core3h commands e.g. core3h_destination(...)

Some examples:

.. list-table:: dbbc3 vs. python commands
   :widths: 25 25
   :header-rows: 1

   * - dbbc3 command
     - python command
   * - time
     - dbbc3.time()
   * - dbbcifa=2,10
     - dbbc3.dbbcif('A', 2, mode=10)
   * - core3h=1,sysstat
     - dbbc3.core3h_sysstat(0)
   * - adb3l=reseth
     - dbbc3.adb3l_reseth()

----------------------
Core3h board numbering
----------------------

Unlike in the the DBBC3 control software the python packages numbers the core3h boards starting from 0. Alternatively all methods expecting a core board number except characters ('A' = 0, 'B' = 1 etc.)
