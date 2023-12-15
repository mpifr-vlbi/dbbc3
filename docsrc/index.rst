.. dbbc3 documentation master file, created by
   sphinx-quickstart on Mon Mar 23 15:20:54 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

dbbc3 - python control of the DBBC3 VLBI backend
************************************************

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


DBBC3 Module Reference
----------------------

    * :mod:`dbbc3.DBBC3`
    * :mod:`dbbc3.DBBC3Commandset.DBBC3Commandset`
        * :mod:`dbbc3.DBBC3Commandset.DBBC3Commandset_DDC_U_126`
        * :mod:`dbbc3.DBBC3Commandset.DBBC3Commandset_DDC_U_125`
        * :mod:`dbbc3.DBBC3Commandset.DBBC3Commandset_DDC_V_124`
        * :mod:`dbbc3.DBBC3Commandset.DBBC3Commandset_DDC_L_121`
        * :mod:`dbbc3.DBBC3Commandset.DBBC3Commandset_DSC_110`
        * :mod:`dbbc3.DBBC3Commandset.DBBC3Commandset_OCT_D_110`
        * :mod:`dbbc3.DBBC3Commandset.DBBC3Commandset_OCT_D_120`
    * :mod:`dbbc3.DBBC3Config`
    * :mod:`dbbc3.DBBC3Util`
    * :mod:`dbbc3.DBBC3Validation`
        * :mod:`dbbc3.DBBC3Validation.DBBC3ValidationDefault`
        * :mod:`dbbc3.DBBC3Validation.DBBC3Validation_OCT_D_110`
        * :mod:`dbbc3.DBBC3Validation.DBBC3Validation_OCT_D_120`

    * :mod:`dbbc3.DBBC3Multicast`


Links
-----
    * `Github project pages <https://github.com/mpifr-vlbi/dbbc3/>`_
    * `HatLab web pages <https://www.hat-lab.cloud/>`_



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

