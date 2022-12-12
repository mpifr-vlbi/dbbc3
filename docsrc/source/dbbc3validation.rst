:mod:`DBBC3Validation` Module
-----------------------------

.. automodule:: dbbc3.DBBC3Validation
    :member-order: groupwise


A very simple example:

.. code-block:: python

        from dbbc3.DBBC3 import DBBC3
        from dbbc3.DBBC3Validation import ValidationFactory, ValidationReport
        import logging

        dbbc3 = DBBC3("dbbc3")

        val = ValidationFactory().create(dbbc3)

        # print validation result
        print (val.validateIFLevel("A"))

        # log validation result
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger(__name__)
        rep = val.validateIFLevel("A")
        rep.log(logger)


:py:class:`Item` class
----------------------

.. autoclass:: dbbc3.DBBC3Validation.Item
    :members: 

:py:class:`ValidationReport` class
----------------------------------

.. autoclass:: dbbc3.DBBC3Validation.ValidationReport
    :members: 
    :member-order: groupwise

:py:class:`ValidationFactory` class
-----------------------------------

.. autoclass:: dbbc3.DBBC3Validation.ValidationFactory
    :members: 
    :member-order: groupwise

