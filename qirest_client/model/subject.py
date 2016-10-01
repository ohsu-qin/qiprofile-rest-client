"""
The qiprofile subject Mongodb data model.
"""

import re
import mongoengine
from mongoengine import (fields, signals)
from .. import choices
from .common import Encounter
from .imaging import (Scan, Session)
from .clinical import Treatment


class Project(mongoengine.Document):
    """The imaging project."""

    meta = dict(collection='qiprofile_project')

    name = fields.StringField(required=True)
    """The required project name."""

    description = fields.StringField()
    """The optional short description."""


class ImagingCollection(mongoengine.Document):
    """The imaging collection."""

    meta = dict(collection='qiprofile_collection')

    project = fields.StringField(required=True)
    """The required project name."""

    name = fields.StringField(required=True)
    """The required collection name."""

    description = fields.StringField()
    """The optional short description."""

    url = fields.StringField()
    """The hyperlink url to additional information."""


class Subject(mongoengine.Document):
    """The patient."""

    RACE_CHOICES = [('White', 'White'),
                    ('Black', 'Black or African American'),
                    ('Asian', 'Asian'),
                    ('AIAN', 'American Indian or Alaska Native'),
                    ('NHOPI', 'Native Hawaiian or Other Pacific Islander')]
    """The standard FDA race categories, in order of US incidence."""

    ETHNICITY_CHOICES = [('Hispanic' , 'Hispanic or Latino'),
                         ('Non-Hispanic' , 'Not Hispanic or Latino')]
    """The standard FDA ethnicity categories."""

    GENDER_CHOICES = ['Male', 'Female']
    """The Male and Female genders."""

    meta = dict(collection='qiprofile_subject')

    project = fields.StringField(required=True)
    """The required project name."""

    collection = fields.StringField(required=True)
    """The required collection name."""

    number = fields.IntField(required=True)
    """The required subject number."""

    birth_date = fields.DateTimeField()
    """The subject date of birth, anonymized to July 7 for deidentified data."""

    diagnosis_date = fields.DateTimeField()
    """The date of the first recorded lesion diagnosis."""

    races = fields.ListField(
        fields.StringField(
            max_length=choices.max_length(RACE_CHOICES),
            choices=RACE_CHOICES))
    """The :const:`RACE_CHOICES` controlled value."""

    ethnicity = fields.StringField(
        max_length=choices.max_length(ETHNICITY_CHOICES),
        choices=ETHNICITY_CHOICES)
    """The :const:`ETHNICITY_CHOICES` controlled value."""

    gender = fields.StringField(
        max_length=choices.max_length(GENDER_CHOICES),
        choices=GENDER_CHOICES)
    """The :const:`GENDER_CHOICES` controlled value."""

    treatments = fields.ListField(field=fields.EmbeddedDocumentField(Treatment))
    """The list of subject treatments."""

    encounters = fields.ListField(field=fields.EmbeddedDocumentField(Encounter))
    """The list of subject encounters in temporal order."""

    @property
    def sessions(self):
        """
        :return: the :class:`qirest_client.imaging.Session`
            encounters
        """
        return (enc for enc in self.encounters if self._is_session(enc))

    def add_encounter(self, encounter):
        """
        Inserts the given encounter to this :class:`Subject` encounters
        list in temporal order by encounter date.
        """
        index = next((i for i, enc in enumerate(self.encounters)
                      if enc.date > encounter.date), len(self.encounters))
        # Add the new encounter to the subject encounters list.
        self.encounters.insert(index, encounter)

    @property
    def clinical_encounters(self):
        """
        :return: the non-:class:`qirest_client.imaging.Session`
            encounters
        """
        return (enc for enc in self.encounters if not self._is_session(enc))

    def pre_delete(cls, sender, document, **kwargs):
        """Cascade delete the subject's sessions."""

        for sess in self.sessions:
            sess.delete()

    def _is_session(self, encounter):
        return isinstance(encounter, Session)

    def __str__(self):
        return ("%s %s Subject %d" %
                (self.project, self.collection, self.number))

signals.pre_delete.connect(Subject.pre_delete, sender=Subject)
