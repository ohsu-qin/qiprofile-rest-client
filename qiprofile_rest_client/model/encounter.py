"""
The qiprofile encounter abstract MongoDB data model.
"""

import mongoengine
from mongoengine import (fields, ValidationError)


class Encounter(mongoengine.EmbeddedDocument):
    """The patient clinical encounter, e.g. biopsy."""

    meta = dict(allow_inheritance=True)

    date = fields.DateTimeField(required=True)

    weight = fields.IntField()
    """The integer weight in kilograms."""
