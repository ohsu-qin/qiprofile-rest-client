"""
The qiprofile encounter abstract MongoDB data model.
"""

import mongoengine
from mongoengine import (fields, ValidationError)


class Encounter(mongoengine.EmbeddedDocument):
    """The patient clinical encounter, e.g. biopsy or imaging session."""

    meta = dict(allow_inheritance=True)

    date = fields.DateTimeField(required=True)
    """The encounter date."""

    weight = fields.IntField()
    """The patient weight in kilograms."""
