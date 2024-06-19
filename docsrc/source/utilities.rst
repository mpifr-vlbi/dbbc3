=========
Utilities
=========

The following python scripts are provided:

=========================== =======
utility                     purpose
=========================== =======
dbbc3client.py              An interactive client for communicating with the DBBC3
dbbc3ctl.py                 A general purpose tool to validate the state of the DBBC3 system or its sub-systems
dbbc3mon.py                 A GUI tool for monitoring the DBBC3 (requires multicast)
dbbc3_powerlogger.py        Logs the DBBC3 power readings (requires multicast)
convert_powerlog_to_HDF5.py Convert the DBBC3 power log files to HDF5 format
dbbc3_ppslogger.py          Logs the DBBC3 PPS delays (requires multicast)
=========================== =======

dbbc3ctl.py
-----------

This script validates the state of the DBBC3 system.

**Interactive Mode:**

.. code-block:: python

  > ./dbbc3ctl.py 134.104.30.223
  === Trying to connect to 134.104.30.223:4000
  Selecting commandset version: DBBC3Commandset_DDC_U_126
  === Connected
  === DBBC3 is running: mode=DDC_U version=126(221103)
  === Using boards: [0, 1]
  Welcome to the DBBC3.  Type help or ? to list commands
  (dbbc3ctl): ?
  check recorder @host @interface
  check sampler offset [all,0,1]
  check sampler gain [all,0,1]
  check sampler phase [all,0,1]
  check timesync [all,0,1]
  check synthesizer lock [all,0,1]
  check synthesizer freq [all,0,1]
  check bstate [all,0,1]
  check pps
  check system [all,0,1]
  get version

**Full system validation:**

.. code-block:: python

  > ./dbbc3ctl.py 134.104.30.223
  === Trying to connect to 134.104.30.223:4000
  Selecting commandset version: DBBC3Commandset_DDC_U_126
  === Connected
  === DBBC3 is running: mode=DDC_U version=126(221103)
  === Using boards: [0, 1]
  Welcome to the DBBC3.  Type help or ? to list commands
  (dbbc3ctl): check system all
  ...
  
  [OK] === Checking sampler phases -
  === Checking board 0
  [OK] === Checking 1PPS synchronisation < +- 200 ns - PPS delays: [16, 16] ns
  [OK] === Checking time synchronisation of core board A - Reported time: 2023-01-24 12:53:38
  [OK] === Checking synthesizer lock state of board A - Locked
  [OK] === Checking GCoMo synthesizer frequency of board A - Freq=9000.000000 MHz
  [WARNING][FAIL]/[WARN] === Checking IF power level on core board A - IF input power is too low. The attenuation should be in the range 20-40, but is 4
  [RESOLUTION] Increase the IF power
  ...

**Scripted Mode:**

Execute a single command:

.. code-block:: python

  > ./dbbc3ctl.py -c "check synthesizer lock" 134.104.30.223

Execute multiple commands:

.. code-block:: python

  > ./dbbc3ctl.py -c "check synthesizer lock" –c "check synthesizer freq" 134.104.30.223

Execute commands multiple times (e.g. 10):

.. code-block:: python

  > ./dbbc3ctl.py -c "check synthesizer lock" –r 10 134.104.30.223

