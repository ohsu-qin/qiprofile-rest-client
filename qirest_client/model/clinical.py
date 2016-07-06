"""
The qiprofile clinical Mongodb data model.
"""

import re
import math
import mongoengine
from mongoengine import (fields, ValidationError)
from .. import choices
from .common import (Encounter, Outcome, TumorExtent)

POS_NEG_CHOICES = [(True, 'Positive'), (False, 'Negative')]
"""The Boolean choices for Positive/Negative display values."""

YES_NO_CHOICES = [(True, 'Yes'), (False, 'No')]
"""The Boolean choices for Yes/No display values."""


class Agent(mongoengine.EmbeddedDocument):
    """A treatment agent, e.g. drug or radiation."""

    meta = dict(allow_inheritance=True)


class Drug(Agent):

    name = fields.StringField(required=True)
    """The official listed drug name."""


class Radiation(Agent):

    BEAM_TYPES = ['photon', 'proton', 'electron', 'neutron', 'carbon']
    """
    The radiation beam type controlled values.
    """

    beam_type = fields.StringField(choices=BEAM_TYPES)


class OtherAgent(Agent):

    name = fields.StringField(required=True)


class Dosage(mongoengine.EmbeddedDocument):
    """The agent dosage."""

    agent = fields.EmbeddedDocumentField(Agent, required=True)
    """The administered Drug or Radiation."""

    amount = fields.FloatField(required=True)
    """
    The cumulative amount of the agent administered over the
    course of the duration, normalized by weight.
    
    For chemotherapy, the field unit is milligrams per kilogram
    (mg/kg).
    
    For radiotherapy, the field unit is Greys per kilogram (Gy/kg).
    
    Radiation fractions and daily chemotherapy dosages are not tracked.
    """

    start_date = fields.DateTimeField()
    """The first date the agent is administered."""

    duration = fields.IntField()
    """
    The span in days during which the agent is administered.
    """


class Treatment(mongoengine.EmbeddedDocument):
    """
    The patient therapy, e.g. adjuvant. Treatment is one of
    the :const:`Treatment.TYPE_CHOICES` types, and occurs over
    a period of time. The treatment consists of dosages, which
    may be pharmocological or radiological.
    """

    TYPE_CHOICES = ('Neoadjuvant', 'Primary', 'Adjuvant')

    treatment_type = fields.StringField(choices=TYPE_CHOICES)

    start_date = fields.DateTimeField(required=True)

    end_date = fields.DateTimeField(required=True)

    dosages = fields.ListField(
        field=mongoengine.EmbeddedDocumentField(Dosage)
    )


class Grade(mongoengine.EmbeddedDocument):
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


class FNCLCCGrade(Grade):
    """
    The `FNCLCC <http://www.iarc.fr/en/publications/pdfs-online/pat-gen/bb5/bb5-classifsofttissue.pdf>`_
    sarcoma tumor grade."""

    differentiation = fields.IntField(choices=range(1, 4))

    necrosis_score = fields.IntField(choices=range(0, 3))

    mitotic_count = fields.IntField(choices=range(1, 4))


def necrosis_percent_as_score(necrosis_percent):
    """
    Calculates the necrosis score from the necrosis percent
    according to the
    `Stanford Synovial Sarcoma Guideline<http://surgpathcriteria.stanford.edu/softmisc/synovial_sarcoma/grading.html>`
    as follows:
    * If the percent is None, then None
    * Otherwise, if the percent is 0, then 0
    * Otherwise, if the percent is less than 50, then 1
    * Otherwise, 2
    
    :param necrosis_percent: the integer percent,
        :class:`NecrosisPercentValue` or  :class:`NecrosisPercentRange`
    :return: the necrosis score
    :raise ValidationError: if the percent is a range that spans 50%
    """
    if necrosis_percent == None:
        return None
    # Wrap a simple integer as a trivial range.
    if isinstance(necrosis_percent, int):
        necrosis_range = NecrosisPercentRange(
            start=NecrosisPercentRange.LowerBound(value=necrosis_percent),
            stop=NecrosisPercentRange.UpperBound(value=necrosis_percent + 1)
        )
    # Convert a value to a trivial range for convenience.
    elif isinstance(necrosis_percent, NecrosisPercentValue):
        necrosis_range = NecrosisPercentRange(
            start=NecrosisPercentRange.LowerBound(value=necrosis_percent.value),
            stop=NecrosisPercentRange.UpperBound(value=necrosis_percent.value + 1)
        )
    elif isinstance(necrosis_percent, NecrosisPercentRange):
        necrosis_range = necrosis_percent
    else:
        raise ValidationError("Necrosis percent type is not supported: %s" %
                              necrosis_percent.__class__)
    if necrosis_range.stop.value == 1:
        return 0
    elif necrosis_range.stop.value <= 50:
        return 1
    elif necrosis_range.start.value >= 50:
        return 2
    else:
        raise ValidationError("The necrosis percent score cannot be"
                              " determined from the range" % necrosis_range)


class NecrosisPercent(Outcome):
    """The necrosis percent value or range."""

    meta = dict(allow_inheritance=True)


class NecrosisPercentValue(NecrosisPercent):
    """The necrosis percent absolute value."""

    value = fields.IntField(choices=range(0, 101))


class NecrosisPercentRange(NecrosisPercent):
    """
    The necrosis percent range.
    
    :Note: it is recommended, although not required, that the percent
        range is a decile range, e.g. [20-30].
    
    :Note: A range which spans 50%, e.g. [40-60], results in a
        :meth:`necrosis_percent_as_score` ValidationError.
    """

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
    
    def __repr__(self):
        return "%d-%d" % (self.start, self.stop)


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
            ^(
             (?P<prefix>c|p|y|r|a|u)?   # The prefix modifier
             T)?                        # The size designator
            (x |                        # Size cannot be evaluated
             (?P<in_situ>is) |          # Carcinoma in situ
             ((?P<tumor_size>0|1|2|3|4) # The size
              (?P<suffix>a|b|c)?        # The suffix modifier
             )
            )$
        """
        """
        The tumor size pattern.
        
        Examples:
        * ``T3``
        * ``pT2`` - pathology prefix
        * ``T3a`` - ``a``, ``b`` or ``c`` suffix modifier is allowed
        * ``3a`` - ``T`` prefix is optional for the size alone
        * ``Tx`` - tumor size cannot be evaluated
        * ``Tis`` - in situ
        """

        SIZE_REGEX = re.compile(SIZE_PAT, re.VERBOSE)
        """The :const:`SIZE_PAT` pattern regular expression."""

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
            Parses the given string into a new Size. The size must match
            the :const:`SIZE_REGEX` regular expression.

            :param value: the input string
            :return: the new Size object
            :raise ValidationError: it the size value string does not
                match :const:`SIZE_REGEX`
            """
            match = klass.SIZE_REGEX.match(value)
            if not match:
                raise ValidationError("TNM Size value is not supported:"
                                      " %s" % value)
            
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

    grade = fields.EmbeddedDocumentField(Grade)

    serum_tumor_markers = fields.IntField(choices=range(0, 4))

    resection_boundaries = fields.IntField(choices=range(0, 3))

    lymphatic_vessel_invasion = fields.BooleanField(choices=POS_NEG_CHOICES)

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


class HormoneReceptorStatus(Outcome):
    """The patient estrogen/progesterone hormone receptor status."""

    class IntensityField(fields.IntField):
        def validate(self, value, clean=True):
            return value > 0 and value <= 100

    hormone = fields.StringField(required=True)

    positive = fields.BooleanField(choices=YES_NO_CHOICES)

    quick_score = fields.IntField(choices=range(0, 9))

    intensity = IntensityField()


class BreastNormalizedAssayField(fields.IntField):
    """The normalized Breast genomics result in the inclusive range [0, 15]."""

    def validate(self, value, clean=True):
        return value > 0 and value <= 15


class BreastNormalizedAssay(mongoengine.EmbeddedDocument):
    """The Breast genomics panel normalized to reference genes."""

    class HER2(mongoengine.EmbeddedDocument):
        grb7 = BreastNormalizedAssayField()
        her2 = BreastNormalizedAssayField()

    class Estrogen(mongoengine.EmbeddedDocument):
        er = BreastNormalizedAssayField()
        pgr = BreastNormalizedAssayField()
        bcl2 = BreastNormalizedAssayField()
        scube2 = BreastNormalizedAssayField()

    class Proliferation(mongoengine.EmbeddedDocument):
        ki67 = BreastNormalizedAssayField()
        stk15 = BreastNormalizedAssayField()
        survivin = BreastNormalizedAssayField()
        ccnb1 = BreastNormalizedAssayField()
        mybl2 = BreastNormalizedAssayField()

    class Invasion(mongoengine.EmbeddedDocument):
        mmp11 = BreastNormalizedAssayField()
        ctsl2 = BreastNormalizedAssayField()

    gstm1 = BreastNormalizedAssayField()

    cd68 = BreastNormalizedAssayField()

    bag1 = BreastNormalizedAssayField()

    her2 = fields.EmbeddedDocumentField(HER2)

    estrogen = fields.EmbeddedDocumentField(Estrogen)

    proliferation = fields.EmbeddedDocumentField(Proliferation)

    invasion = fields.EmbeddedDocumentField(Invasion)


class BreastGeneticExpression(Outcome):
    """The breast patient genetic expression results."""

    HER2_NEU_IHC_CHOICES = [(0, '0'), (1, '1+'), (2, '2+'), (3, '3+')]
    """The HER2 NEU IHC choices are displayed as 0, 1+, 2+, 3+."""

    class KI67Field(fields.IntField):
        def validate(self, value, clean=True):
            return value >= 0 and value <= 100

    her2_neu_ihc = fields.IntField(choices=HER2_NEU_IHC_CHOICES)

    her2_neu_fish = fields.BooleanField(choices=POS_NEG_CHOICES)

    ki67 = KI67Field()

    normalized_assay = fields.EmbeddedDocumentField(BreastNormalizedAssay)


class Evaluation(mongoengine.EmbeddedDocument):
    """The patient evaluation holds outcomes."""

    meta = dict(allow_inheritance=True)


class TumorLocation(mongoengine.EmbeddedDocument):
    """The tumor body part and directional orientation."""

    SAGITTAL_CHOICES = ('Left', 'Right')

    CORONAL_CHOICES = ('Anterior', 'Posterior')

    body_part = fields.StringField()
    """
    The capitalized body part, e.g. ``Thigh``.
    
    This field is only required when the tumor type is not localized
    to a body part, e.g. sarcoma.
    """

    sagittal_location = fields.StringField(choices=SAGITTAL_CHOICES)

    coronal_location = fields.StringField(choices=CORONAL_CHOICES)


class TumorPathology(mongoengine.EmbeddedDocument):
    """The tumor-specific pathology."""

    meta = dict(allow_inheritance=True)

    location = fields.EmbeddedDocumentField(TumorLocation)

    tnm = fields.EmbeddedDocumentField(TNM)
    
    extent = fields.EmbeddedDocumentField(TumorExtent)
    """The primary tumor bed volume measured by the pathologist."""


class PathologyReport(Evaluation):
    """The patient pathology report findings."""

    tumors = fields.ListField(fields.EmbeddedDocumentField(TumorPathology))
    """
    The tumor pathology findings. The tumors list order is
    the same as the :class:`qirest-client.model.imaging.Scan`
    ``rois`` list order. The most significant tumor is preferably
    listed first.
    """


class ResidualCancerBurden(mongoengine.EmbeddedDocument):
    """The residual cancer burden after neodjuvant treatment."""

    tumor_cell_density = fields.IntField()
    """The primary tumor bed cancer cellularity percent."""

    dcis_cell_density = fields.IntField()
    """
    The percent of the primary tumor bed that contains invasive
    carcinoma.
    """

    positive_node_count = fields.IntField()
    """The number of metastasized axillary lymph nodes."""

    total_node_count = fields.IntField()
    """The total number of axillary lymph nodes."""

    largest_nodal_metastasis_length = fields.IntField()
    """The diameter of the largest axillary lymph node metastasis."""


class BreastPathology(TumorPathology):
    """The QIN breast patient pathology summary."""

    hormone_receptors = fields.ListField(
        field=mongoengine.EmbeddedDocumentField(HormoneReceptorStatus)
    )

    genetic_expression = fields.EmbeddedDocumentField(BreastGeneticExpression)

    rcb = fields.EmbeddedDocumentField(ResidualCancerBurden)

    def rcb_index(self):
        """
        Returns the RCB index per
        `JCO 25:28 4414-4422 <http://jco.ascopubs.org/content/25/28/4414.full>`_.
        """
        # The bidimensional tumor size metric.
        size = math.sqrt(self.extent.length * self.extent.width)
        # The overall tumor cellularity.
        overall = float(self.rcb.tumor_cell_density) / 100
        # The in situ cellularity.
        in_situ = float(self.rcb.dcis_cell_density) / 100
        # The invasive carcinoma proportion.
        invasion = (1 - in_situ) * overall
        # The RCB index invasion component.
        invasion_factor = 1.4 * math.pow(invasion * size, 0.17)
        # The RCB index positive node component.
        pos_node_factor = 1 - math.pow(0.75, self.rcb.positive_node_count)
        # The base of the RCB index node component.
        node_base = 4 * pos_node_factor * self.rcb.largest_nodal_metastasis_length
        # The RCB index node component.
        node_factor =  math.pow(node_base, 0.17)

        # The RCB index is the sum of the invasion and node components.
        return invasion_factor + node_factor 

    def rcb_class(self, rcb_index):
        """
        Returns the RCB class per the cut-offs defined in
        `JCO 25:28 4414-4422 <http://jco.ascopubs.org/content/25/28/4414.full>`_.
        
        :param rcb_index: the :meth:`rcb_index` value
        """
        if rcb_index == 0:
            return 0
        elif rcb_index < 1.36:
            return 1
        elif rcb_index < 3.28:
            return 2
        else:
            return 3


class SarcomaPathology(TumorPathology):
    """The QIN sarcoma patient pathology summary."""

    HISTOLOGY_CHOICES = ('Carcinosarcoma', 'Cerebellar', 'Chondrosarcoma',
                         'Clear Cell', 'Dermatofibrosarcoma', 'Fibrosarcoma',
                         'Leiomyosarcoma', 'Liposarcoma', 'MFH', 'MPNST',
                         'Osteosarcoma', 'Rhabdomyosarcoma', 'Synovial', 'Other')
    """The histology controlled values."""

    histology = fields.StringField(choices=HISTOLOGY_CHOICES)

    necrosis_percent = fields.EmbeddedDocumentField(NecrosisPercent)


class Biopsy(Encounter):
    """
    Non-therapeutic tissue extraction resulting in a pathology report.
    """

    pathology = fields.EmbeddedDocumentField(PathologyReport, required=True)


class Surgery(Encounter):
    """
    Therapeutic tissue extraction which usually results in a pathology report.
    """

    meta = dict(allow_inheritance=True)

    pathology = fields.EmbeddedDocumentField(PathologyReport)


class BreastSurgery(Surgery):
    """Breast tumor extraction."""

    TYPE_CHOICES = ('Total Mastectomy', 'Partial Mastectomy', 'Lumpectomy')
    """The surgery type controlled values."""

    surgery_type = fields.StringField(choices=TYPE_CHOICES)
