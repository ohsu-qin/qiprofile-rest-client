"""
The qiprofile unit of measurement MongoDB data model.

This uom module is an advisory module for quantity display and
conversion. Quantities are always stored in a canonical unit
documented in the field.
"""

import decimal
from numbers import Number
import mongoengine
from mongoengine import fields


class Decimal(mongoengine.EmbeddedDocument):
    """
    This Decimal document class is a work-around for the broken
    MongoEngine DecimalField
    (cf. https://github.com/MongoEngine/mongoengine/issues?q=is%3Aissue+is%3Aopen+decimal).

    Decimal has a float value and an optional precision. The default
    precision is determined as follows:

    * If the Decimal value is initialized with a python ``decimal.Decimal``
      or string, then the default precision is the number of decimal places
      expressed in that value, e.g.::

          Decimal('1.24').precision #=> 2
          Decimal(decimal.Decimal('1.4')).precision #=> 1

    * If the Decimal value is initialized with an integer, then the default
            precision is zero, e.g.::

                Decimal(1).precision #=> 0
    """
    # TODO - migrate to DecimalField when it is fixed in MongoEngine.

    def __init__(self, *args, **kwargs):
        # The positional arguments will be replaced by keyword arguments.
        if args:
            value = args[0]
            if len(args) > 1:
                precision = args[1]
            else:
                precision = None
        else:
            value = kwargs.get('value')
            precision = kwargs.get('precision')

        # Convert the value to a float, if necessary.
        if value != None:
            value = float(value)
        # Set the value keyword argument.
        kwargs['value'] = value

        # If the precision is not specified, then determine a default if
        # possible.
        if precision == None:
            if isinstance(value, decimal.Decimal):
                value_s = str(value)
                if '.' in value_s:
                    _, precision_s = value_s.split('.')
                    precision = int(precision_s)
            elif isinstance(value, int):
                precision = 0

        # Set the precision keyword argument.
        kwargs['precision'] = precision

        super(Decimal, self).__init__(**kwargs)

    def canonical(self):
        """
        :return: the python decimal.Decimal equivalent of this Decimal
        """
        return decimal.Decimal(str(value))

    def __repr__(self):
        """
        :return: the value as a string with decimal places truncated
            by the precision
        """
        if self.precision == None:
            return str(self.value)
        elif self.precision == 0:
            return str(int(self.value))
        else:
            pat = '%.' + ("%s" % self.precision) + 'f'
            return pat % self.value

    value = fields.FloatField(required=True)

    precision = fields.IntField()


class Unit(mongoengine.EmbeddedDocument):
    """
    Unit is an abstract class for the supported measurement units.
    Each unit has a scaling factor with the default scaling factor
    defined in the concrete Unit subclass. Each Unit subclass has
    the following class variables:

    * ``BASE`` - the standard unscaled metric unit abbreviation,
      e.g. ``m`` for the meter Extent unit.

    * ``SCALES`` - the recommended scaling factors, e.g. ``m`` for
       milli and ``c`` for centi.

    The scales are a list in preference order, e.g. the ``Extent.SCALES``
    value ``['c', 'm']`` implies that the preferred extent unit display
    is ``cm`` (centimeter) and an edit form should show the scales ``c``
    and ``m``, in that order, defaulting to ``c``. A scale of None
    signifies the scaling factor 1, e.g. the  the ``Radiation.SCALES``
    value ``[None, 'c']`` implies that the preferred radiation unit
    display is ``Gy`` (Gray) and an edit form should show the scales
    blank and ``c``, in that order, defaulting to blank (scaling factor
    1).

    These class variables are advisory. The client is responsible for
    displaying the base and scales and converting from a scaled value
    to an unscaled value before saving the measurement to the database.
    """

    meta = dict(allow_inheritance=True)


class Extent(Unit):

    SCALES = ['c', 'm']

    BASE = 'm'
    """The meter designator."""

    scale = fields.StringField(default='c')
    """The default extent is centimeter."""


class Weight(Unit):

    SCALES = ['m', 'k']

    BASE = 'g'
    """The gram designator."""

    scale = fields.StringField(default='m')
    """The default weight is milligram."""


class Volume(Unit):

    SCALES = ['m']

    BASE = 'l'
    """The liter designator."""

    scale = fields.StringField(default='m')
    """The default volume is milliliter."""


class Radiation(Unit):
    """The radiation unit is always an unscaled Gray."""

    BASE = 'Gy'
    """The Gray designator."""

class Measurement(mongoengine.EmbeddedDocument):
    """
    A scientific measurement.

    The measurement is a quantitative amount associated with a unit.
    The unit is the Unit as captured and displayed. The amount is
    expressed as a python Decimal in unscaled units. If the constructor
    is called with a non-Decimal numeric amount, then the value is
    converted to a Decimal, e.g.::

        Measurement(amount=0.006, unit=Weight())

    is equivalent to::

        from decimal import Decimal
        Measurement(amount=Decimal(0.006), unit=Weight())

    The measurement unit can be qualified by a second ``per_unit``
    dimension, e.g. 2 mg/kg dosage per patient weight is expressed
    as::

        Measurement(amount=0.002, unit=Weight(), per_unit=Weight(scale='k'))

    :Note: the amount is a :class:`Decimal` embedded object rather than
      the broken MongoEngine ``DecimalField`` (see the :class:`Decimal`
      comment).
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the Measurement document. The amount can be either
        a positional or a keyword argument. The amount is converted to
        a Decimal.
        
        :param args: the amount as a positional argument
        :param kwargs: the following keyword arguments:
        :keyword amount: the amount as a keyword argument
        """
        # Convert the amount to a Decimal, if necessary. The amount
        # can be the first positional argument or a keyword argument.
        if args:
            args = list(args)
            args[0] = self._as_decimal(args[0])
        elif 'amount' in kwargs:
            kwargs['amount'] = self._as_decimal(kwargs['amount'])
        
        super(Measurement, self).__init__(*args, **kwargs)

    def _as_decimal(self, value):
        if isinstance(value, Number):
            return Decimal(value)
        else:
            return value

    amount = fields.EmbeddedDocumentField(Decimal, required=True)

    unit = fields.EmbeddedDocumentField(Unit)

    per_unit = fields.EmbeddedDocumentField(Unit)
