==========
Validation
==========

The :mod:`DBBC3` package provides higher level validation methods via the :py:class:`dbbc3.DBBC3Validation` module e.g. for:

- Checking IF settings
- Checking sampler settings
- Checking synthesizer settings

.. code-block:: python

  from dbbc3.DBBC3 import DBBC3
  from dbbc3.DBBC3Validation import ValidationFactory

  dbbc3 = DBBC3("134.104.30.223")
  valFactory = ValidationFactory()
  val = valFactory.create(dbbc3, True)

  val.validateSynthesizerLock(0)

Validation methods return a :py:class:`dbbc3.DBBC3Validation.ValidationReport` object.

The ValidationReport can contain multiple entries of type :py:class:`dbbc3.DBBC3Validation.Item`.

Item properties
---------------

  action:     a description of what was validated

  state:      the outcome of the the validation

  level:      the logging level of the validation

  message:    the validation outcome message

  exit:       True if the validation should trigger and exit event

  resolution: A message describing possible solutions for failed validations


An example response for validating the synthesizer lock status:

.. code-block:: python

  rep = val.validateSynthesizerLock(0)
  print(rep)

  action:	=== Checking synthesizer lock state of board A
  state:	OK
  level:	INFO
  message:	Locked
  exit:		False
  resolution:	...

  

