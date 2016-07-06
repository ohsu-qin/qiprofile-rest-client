"""
The data model classes common to both imaging and clinical observations.
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


class Outcome(mongoengine.EmbeddedDocument):
    """The result of a patient clinical or imaging observation."""

    meta = dict(allow_inheritance=True)


class TumorExtent(Outcome):
    """The tumor 3D measurements in millimeters."""

    length = fields.IntField()
    """The longest tumor convex hull diameter length."""

    width = fields.IntField()
    """
    The longest tumor convex hull diameter perpendicular to the
    length segment.
    """

    depth = fields.IntField()
    """
    The longest tumor convex hull diameter perpendicular to the
    length and width segments.
    """
