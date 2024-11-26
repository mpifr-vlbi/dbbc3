=========
Multicast
=========

The DBBC3 sends multicast messages containing its current state on a one second cadence.

Supported software versions:

- DSC versions >= 120
- DDC versions >= 125
- OCT version >= 120

The content of the multicast message is mode-dependent

Multicast Processing
--------------------

The dbbc3 package provides the :py:class:`dbbc3.DBBC3Multicast` module which handles processing of multicast messages

.. code-block:: python

  from dbbc3.DBBC3Multicast import DBBC3MulticastFactory

  mcFactory = DBBC3MulticastFactory()
  mc = mcFactory.create()

  message = mc.poll()

The multicast message is returned as a dictionary.

Example multicast message dict (OCT_D mode):

.. code-block:: python

  {'mode': 'OCT_D’, 'majorVersion': 120, 'minorVersionString': 'August 31st 2022', 'minorVersion': 220831, 'boardPresent': [True, True, True, True, False, False, False, False], 'boardActive': [True, True, True, True, False, False, False, False], 'if_1': {'mode': 'agc', 'attenuation': 11, 'count': 31882, 'target': 32000, 'synth': {'status': 1, 'lock': 1, 'attenuation': 18, 'frequency': 4524.0}, 'sampler0': {'power': 72746343, 'offset': 64410282}, 'sampler1': {'power': 73962686, 'offset': 63665610}, 'sampler2': {'power': 73158462, 'offset': 63718535}, 'sampler3': {'power': 73743109, 'offset': 63949517}, 'delayCorr': (147462423, 144809580, 148870960), 'vdiftime': 2058959, 'vdifepoch': 46, 'ppsdelay': 999999984, 'filter1': {'power': 121762240, 'stats': (22683397, 41360632, 41210614, 22745357), 'statsFrac': (17.72140390625, 32.312993750000004, 32.1957921875, 17.76981015625)}, 'filter2': {'power': 166743416, 'stats': (21283596, 41831470, 40420110, 24464824), 'statsFrac': (16.627809375, 32.6808359375, 31.5782109375, 19.11314375)}},
  …
