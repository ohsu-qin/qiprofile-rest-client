"""
The qiprofile clinical Mongodb data model.
"""

import re
import mongoengine
from mongoengine import (fields, ValidationError)
from .. import choices
from .uom import Measurement

POS_NEG_CHOICES = [(True, 'Positive'), (False, 'Negative')]
"""The Boolean choices for Positive or Negative status."""


class Treatment(mongoengine.EmbeddedDocument):
    """The patient therapy, e.g. adjuvant."""

    TYPE_CHOICES = ('Neoadjuvant', 'Primary', 'Adjuvant')

    treatment_type = fields.StringField(
        max_length=choices.max_length(TYPE_CHOICES),
        choices=TYPE_CHOICES)

    start_date = fields.DateTimeField(required=True)

    end_date = fields.DateTimeField(required=True)

    dosages = fields.ListField(
        field=mongoengine.EmbeddedDocumentField('Dosage')
    )


class Dosage(mongoengine.EmbeddedDocument):
    """The agent dosage."""

    agent = fields.EmbeddedDocumentField('Agent', required=True)

    amount = fields.EmbeddedDocumentField(Measurement, required=True)

    start_date = fields.DateTimeField()

    times_per_day = fields.IntField()

    duration = fields.IntField()


class Agent(mongoengine.EmbeddedDocument):
    """A treatment agent, e.g. drug or radiation."""

    meta = dict(allow_inheritance=True)


class Drug(Agent):

    name = fields.StringField(required=True)
    """The official listed drug name."""


class Radiation(Agent):

    FORMS = ['photon', 'proton', 'electron', 'neutron', 'carbon ion', 'radiopharmaceutical']
    """
    The advisory radiation forms list. The client should constraion the radiation
    form choices to this list where possible, but allow for free-form text where
    necessary.
    """

    form = fields.StringField()


class OtherAgent(Agent):

    name = fields.StringField(required=True)


class Encounter(mongoengine.EmbeddedDocument):
    """The patient clinical encounter, e.g. biopsy."""

    meta = dict(allow_inheritance=True)

    date = fields.DateTimeField(required=True)


class Biopsy(Encounter):
    """Non-therapeutic tissue extraction resulting in a pathology report."""

    pathology = fields.EmbeddedDocumentField('Pathology', required=True)


class Surgery(Encounter):
    """Therapeutic tissue extraction which usually results in a pathology report."""

    meta = dict(allow_inheritance=True)

    pathology = fields.EmbeddedDocumentField('Pathology')


class Assessment(Encounter):
    """Generic collection of outcomes."""

    evaluation = fields.EmbeddedDocumentField('GenericEvaluation',
                                              required=True)


class BreastSurgery(Surgery):
    """Breast tumor extraction."""

    TYPE_CHOICES = ('Mastectomy', 'Lumpectomy')
    """
    The advisory surgery types list. The client should include these surgery type
    choices, but allow for free-form text where necessary.
    """

    surgery_type = fields.StringField()

    partial = fields.BooleanField(default=False)


class Evaluation(mongoengine.EmbeddedDocument):
    """The patient evaluation holds outcomes."""

    meta = dict(allow_inheritance=True)


class GenericEvaluation(Evaluation):
    """An unconstrained set of outcomes."""

    outcomes = fields.ListField(fields.EmbeddedDocumentField('Outcome'))


class Pathology(Evaluation):
    """The patient pathology summary."""

    meta = dict(allow_inheritance=True)

    tnm = fields.EmbeddedDocumentField('TNM')


class BreastReceptorStatus(mongoengine.EmbeddedDocument):
    """The breast patient hormone receptor results."""
    
    estrogen = fields.EmbeddedDocumentField('HormoneReceptorStatus')

    progesterone = fields.EmbeddedDocumentField('HormoneReceptorStatus')


class BreastGeneticExpression(mongoengine.EmbeddedDocument):
    """The breast patient genetic expression results."""

    HER2_NEU_IHC_CHOICES = [(0, '0'), (1, '1+'), (2, '2+'), (3, '3+')]
    """The HER2 NEU IHC choices are displayed as 0, 1+, 2+, 3+."""

    class KI67Field(fields.IntField):
        def validate(self, value, clean=True):
            return value > 0 and value <= 100

    her2_neu_ihc = fields.IntField(choices=HER2_NEU_IHC_CHOICES)

    her2_neu_fish = fields.BooleanField(choices=POS_NEG_CHOICES)

    ki67 = KI67Field()

    normalized_assay = fields.EmbeddedDocumentField('NormalizedAssay')


class BreastPathology(Pathology):
    """The QIN breast patient pathology summary."""

    hormone_receptors = fields.EmbeddedDocumentField('BreastReceptorStatus')

    genetic_expression = fields.EmbeddedDocumentField('BreastGeneticExpression')


class NormalizedAssayField(fields.IntField):
    """The normalized Breast genomics result in the inclusive range [0, 15]."""

    def validate(self, value, clean=True):
        return value > 0 and value <= 15


class NormalizedAssay(mongoengine.EmbeddedDocument):
    """The Breast genomics panel normalized to reference genes."""

    class HER2(mongoengine.EmbeddedDocument):
        grb7 = NormalizedAssayField()
        her2 = NormalizedAssayField()

    class Estrogen(mongoengine.EmbeddedDocument):
        er = NormalizedAssayField()
        pgr = NormalizedAssayField()
        bcl2 = NormalizedAssayField()
        scube2 = NormalizedAssayField()

    class Proliferation(mongoengine.EmbeddedDocument):
        ki67 = NormalizedAssayField()
        stk15 = NormalizedAssayField()
        survivin = NormalizedAssayField()
        ccnb1 = NormalizedAssayField()
        mybl2 = NormalizedAssayField()

    class Invasion(mongoengine.EmbeddedDocument):
        mmp11 = NormalizedAssayField()
        ctsl2 = NormalizedAssayField()

    gstm1 = NormalizedAssayField()

    cd68 = NormalizedAssayField()

    bag1 = NormalizedAssayField()

    her2 = fields.EmbeddedDocumentField(HER2)

    estrogen = fields.EmbeddedDocumentField(Estrogen)

    proliferation = fields.EmbeddedDocumentField(Proliferation)

    invasion = fields.EmbeddedDocumentField(Invasion)


class SarcomaPathology(Pathology):
    """The QIN sarcoma patient pathology summary."""

    HISTOLOGY_CHOICES = ('Carcinosarcoma', 'Cerebellar', 'Chondrosarcoma',
                         'Clear Cell', 'Dermatofibrosarcoma', 'Fibrosarcoma',
                         'Leiomyosarcoma', 'Liposarcoma', 'MFH', 'MPNST',
                         'Osteosarcoma', 'Rhabdomyosarcoma', 'Synovial', 'Other')
    """
    The advisory histololgy list. The client should constraion the histology
    choices to this list where possible, but allow for free-form text where
    necessary.
    """

    location = fields.StringField()

    necrosis_pct = fields.EmbeddedDocumentField('NecrosisPercent')

    histology = fields.StringField()


## Clinical metrics ##

class Outcome(mongoengine.EmbeddedDocument):
    """The patient clinical outcome."""

    meta = dict(allow_inheritance=True)


class TNM(Outcome):
    """
    The TNM tumor staging. The TNM fields are as follows:

      * size - primary tumor size (T)

      * lymph_status - regional lymph nodes (N)

      * metastasis - distant metastasis (M)

      * grade - tumor grade (G)

      * serum_tumor_markers (S)

      * resection_boundaries (R)

      * lymphatic_vessel_invasion (L)

      * vein_invasion (V)

    The size is an aggregate Size field.
    See http://www.cancer.gov/cancertopics/factsheet/detection/staging for
    an overview. See http://en.wikipedia.org/wiki/TNM_staging_system and
    http://cancerstaging.blogspot.com/ for the value definition.

    :Note: The size and lymph_status choices can be further constrained by
        tumor type. Since :class:`TNM` is a generic class, these constraints
        are not enforced in this TNM class. Rather, the REST client is
        responsible for enforcing additional choice constraints. The
        :meth:`TNM.lymph_status_choices` helper method can be used for
        tumor type specific choices. See :class:`TNM.Size`` for a discussion
        of the size constraints.
  """
    class Size(mongoengine.EmbeddedDocument):
        """
        The TNM primary tumor size field.

        :Note: The size score choices can be further constrained by tumor
            type. For example, the sarcoma tumor_size choices are 0, 1 or 2
            and suffix choices are ``a`` or ``b``. See :class:`TNM` for a
            discussion of choice constraints. The :meth:`TNM.Size.tumor_size_choices`
            and :meth:`TNM.Size.suffix_choices` helper methods can be used for
            tumor type specific choices.
        """

        PREFIXES = ['c', 'p', 'y', 'r', 'a', 'u']

        SUFFIXES = ['a', 'b', 'c']

        SUFFIX_CHOICES = dict(
            Any=['a', 'b', 'c'],
            Sarcoma=['a', 'b']
        )

        TUMOR_SIZE_CHOICES = dict(
            Any=range(0, 5),
            Sarcoma=range(0, 3)
        )

        SIZE_PAT = """
            ^(?P<prefix>c|p|y|r|a|u)?   # The prefix modifier
            T                           # The size designator
            (x |                        # Tumor cannot be evaluated
             (?P<in_situ>is) |          # Carcinoma in situ
             ((?P<tumor_size>0|1|2|3|4) # The size
              (?P<suffix>a|b|c)?        # The suffix modifier
             )
            )$
        """

        @staticmethod
        def tumor_size_choices(tumor_type=None):
            """
            :param tumor_type: the optional tumor type, e.g. ``Breast``
            :return: the tumor_size choices for the given type
            """
            if tumor_type not in TNM.Size.TUMOR_SIZE_CHOICES:
                tumor_type = 'Any'

            return TNM.Size.TUMOR_SIZE_CHOICES[tumor_type]

        @staticmethod
        def suffix_choices(tumor_type=None):
            """
            :param tumor_type: the optional tumor type, e.g. ``Breast``
            :return: the suffix choices for the given type
            """
            if tumor_type not in TNM.Size.SUFFIX_CHOICES:
                tumor_type = 'Any'

            return TNM.Size.SUFFIX_CHOICES[tumor_type]

        SIZE_REGEX = re.compile(SIZE_PAT, re.VERBOSE)
        """The TNM size validation regular expression."""

        prefix = fields.StringField(choices=PREFIXES)

        tumor_size = fields.IntField(choices=TUMOR_SIZE_CHOICES['Any'])

        class InSitu(mongoengine.EmbeddedDocument):
            INVASIVE_TYPE_CHOICES = ('ductal', 'lobular')
            """
            The advisory invasive types list. The client should constraion the invasive
            type choices to this list where possible, but allow for free-form text where
            necessary.
            """

            invasive_type = fields.StringField()

        in_situ = fields.EmbeddedDocumentField(InSitu)

        suffix = fields.StringField(choices=SUFFIX_CHOICES['Any'])

        def __str__(self):
            prefix = self.prefix or ''
            suffix = self.suffix or ''
            if self.in_situ:
                size = 'is'
            elif self.tumor_size:
                size = str(self.tumor_size)
            else:
                size = 'x'

            return "%sT%s%s" % (prefix, size, suffix)

        @classmethod
        def parse(klass, value):
            """
            Parses the given string into a new Size.

            :param value: the input string
            :return: the new Size object
            """
            match = klass.SIZE_REGEX.match(value)
            return klass(**match.groupdict())

        def clean(self):
            """
            Peforms document-level validation.

            :raise ValidationError: if the in_situ flag is set but there
              is a tumor_size or suffix field
            """
            if self.in_situ:
                if self.tumor_size != None:
                    raise ValidationError("TNM Size with in_situ flag set to"
                                          " True cannot have tumor_size %d" %
                                          self.tumor_size)
                if self.suffix != None:
                    raise ValidationError("TNM Size with in_situ flag set to"
                                          " True cannot have a suffix %s" %
                                          self.suffix)
            return True

    LYMPH_STATUS_CHOICES = dict(
        Any=range(0, 4),
        Sarcoma=range(0, 2)
    )

    tumor_type = fields.StringField(required=True)

    size = fields.EmbeddedDocumentField(Size)

    # TODO - make lymph status an aggregate with suffix modifiers,
    # including 'mi'.
    lymph_status = fields.IntField(choices=LYMPH_STATUS_CHOICES['Any'])

    metastasis = fields.BooleanField(choices=POS_NEG_CHOICES)

    grade = fields.EmbeddedDocumentField('Grade')

    serum_tumor_markers = fields.IntField(choices=range(0, 4))

    resection_boundaries = fields.IntField(choices=range(0, 3))

    lymphatic_vessel_invasion = fields.BooleanField()

    vein_invasion = fields.IntField(choices=range(0, 3))

    @staticmethod
    def lymph_status_choices(tumor_type=None):
        """
        :param tumor_type: the optional tumor type, e.g. ``Breast``
        :return: the lymph_status choices for the given type
        """
        if tumor_type not in TNM.LYMPH_STATUS_CHOICES:
            tumor_type = 'Any'

        return TNM.LYMPH_STATUS_CHOICES[tumor_type]


class Grade(Outcome):
    """
    The abstract tumor grade superclass, specialized for each
    tumor type.
    """

    meta = dict(allow_inheritance=True)


class ModifiedBloomRichardsonGrade(Grade):
    """
    The `Modified Bloom Richardson <http://pathology.jhu.edu/breast/grade.php>`_
    (a.k.a. Nottingham) breast tumor grade.
    """

    COMPONENT_CHOICES = range(1, 4)

    tubular_formation = fields.IntField(choices=COMPONENT_CHOICES)

    nuclear_pleomorphism = fields.IntField(choices=COMPONENT_CHOICES)

    mitotic_count = fields.IntField(choices=COMPONENT_CHOICES)


class HormoneReceptorStatus(Outcome):
    """The patient estrogen/progesterone hormone receptor status."""

    class IntensityField(fields.IntField):
        def validate(self, value, clean=True):
            return value > 0 and value <= 100

    hormone = fields.StringField(required=True)

    positive = fields.BooleanField(choices=POS_NEG_CHOICES)

    quick_score = fields.IntField(choices=range(0, 9))

    intensity = IntensityField()


class FNCLCCGrade(Grade):
    """The FNCLCC sarcoma tumor grade."""

    differentiation = fields.IntField(choices=range(1, 4))

    mitotic_count = fields.IntField(choices=range(1, 4))

    necrosis = fields.IntField(choices=range(0, 3))


class NecrosisPercent(Outcome):
    """The necrosis percent value or range."""
    pass


class NecrosisPercentValue(NecrosisPercent):
    """The necrosis percent absolute value."""

    value = fields.IntField(choices=range(0, 101))


class NecrosisPercentRange(NecrosisPercent):
    """The necrosis percent range."""

    class Bound(mongoengine.EmbeddedDocument):
        """
        Necrosis percent upper or lower bound abstract class.
        The subclass is responsible for adding the ``inclusive``
        field.
        """

        meta = dict(allow_inheritance=True)

        value = fields.IntField(choices=range(0, 101))


    class LowerBound(Bound):
        """Necrosis percent lower bound."""

        inclusive = fields.BooleanField(default=True)


    class UpperBound(Bound):
        """Necrosis percent upper bound."""

        inclusive = fields.BooleanField(default=False)

    start = fields.EmbeddedDocumentField(LowerBound)

    stop = fields.EmbeddedDocumentField(UpperBound)
