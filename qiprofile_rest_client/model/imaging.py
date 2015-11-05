"""
The qiprofile imaging Mongodb data model.
"""

import re
import decimal
from numbers import Number
import mongoengine
from mongoengine import (fields, signals, ValidationError)
from .. import choices
from .common import (Encounter, Outcome, TumorExtent)


class VoxelSize(mongoengine.EmbeddedDocument):
    """The voxel width, depth and spacing."""

    width = fields.FloatField()
    """
    The voxel width (= voxel length) in millimeters. For an MR, the width
    is the DICOM Pixel Spacing value.
    """

    depth = fields.FloatField()
    """
    The voxel depth in millimeters. For an MR, the depth is the DICOM
    Slice Thickness.
    """

    spacing = fields.FloatField()
    """
    The inter-slice spacing in millimeters. For an MR, the spacing is
    the DICOM Spacing Between Slices.
    """


class Point(mongoengine.EmbeddedDocument):
    """The 3D point in the volume voxel space."""

    x = fields.IntField()
    """
    The x dimension value in the image coordinate system.
    """

    y = fields.IntField()
    """
    The y dimension value in the image coordinate system.
    """

    z = fields.IntField()
    """
    The z dimension value in the image coordinate system.
    """


class LabelMap(mongoengine.EmbeddedDocument):
    """A label map with an optional associated color lookup table."""

    filename = fields.StringField(required=True)
    """The label map file path relative to the web app root."""

    color_table = fields.StringField()
    """The color map lookup table file path relative to the web app root."""


class Region(mongoengine.EmbeddedDocument):
    """The 3D region in volume voxel space."""

    mask = fields.StringField()
    """The binary mask file name."""

    label_map = fields.EmbeddedDocumentField(LabelMap)
    """The label map file name."""

    centroid = mongoengine.EmbeddedDocumentField(Point)
    """The region centroid."""

    average_intensity = fields.FloatField()
    """The average signal in the region."""


class Volume(mongoengine.EmbeddedDocument):
    """The 3D image volume."""

    filename = fields.StringField(required=True)
    """The image file pathname relative to the web app root."""

    average_intensity = fields.FloatField()
    """The image signal intensity over the entire volume."""


class ImageSequence(Outcome):
    """The scan or registration image volume container."""

    meta = dict(allow_inheritance=True)

    volumes = fields.ListField(field=mongoengine.EmbeddedDocumentField(Volume))
    """The 3D volume images in the sequence."""


class RegistrationProtocol(mongoengine.Document):
    """The registration settings."""

    meta = dict(collection='qiprofile_registration_protocol')

    technique = fields.StringField(required=True)
    """The registration technique, e.g. ``ANTS`` or ``FNIRT``."""

    parameters = fields.DictField()
    """The registration input {parameter: value} dictionary."""


class Registration(ImageSequence):
    """
    The patient image registration that results from processing a scan.
    """

    protocol = fields.ReferenceField(RegistrationProtocol, required=True)
    """The registration protocol."""

    resource = fields.StringField(required=True)
    """The registration imaging store resource name, e.g. ``reg_k3RtZ``."""


class ScanProtocol(mongoengine.Document):
    """
    The scan acquisition protocol. Scans with the same protocol
    and image dimensions are directly comparable, e.g. in comparing
    modeling results across subjects or sessions.
    """

    meta = dict(collection='qiprofile_scan_protocol')

    ORIENTATION = ['axial', 'sagittal', 'coronal']
    """The three imaging axes."""

    scan_type = fields.StringField(required=True)
    """
    The scan type designation controlled value, e.g. ``T1``. The REST update
    client is responsible for ensuring that scan type synonyms resolve to
    the same scan type value, e.g. scans with descriptions including ``t2``,
    ``T2`` and ``T2W`` should all resolve to scan type ``T2``.
    """

    orientation = fields.StringField(choices=ORIENTATION,
                                     max_length=choices.max_length(ORIENTATION))
    """The imaging :const:`ORIENTATION` controlled value."""

    technique = fields.StringField()
    """
    The scan technique, e.g. ``STIR``, ``FLAIR`` or ``BLISS``. The REST update
    client is responsible for ensuring that technique synonyms resolve to the
    same technique value, e.g. scans with descriptions including ``BLISS`` and
    ``BLISS_AUTO_SENSE`` should both resolve to technique ``BLISS``.
    """

    description = fields.StringField()
    """
    The image acquisition scan description, e.g. ``T1 AX SPIN ECHO``.
    This field is customarily specified as the DICOM
    *Series Description* or *Protocol Name* tag. This field is often
    used by the REST update client to infer the controlled vocabulary
    scan type, orientation and technique field values.
    """

    voxel_size = fields.EmbeddedDocumentField(VoxelSize)
    """The voxel size in millimeters."""


class Scan(ImageSequence):
    """
    The the concrete subclass of the abstract :class:`ImageSequence`
    class for scans.
    """

    number = fields.IntField(required=True)
    """
    The scan number. In the XNAT image store, each scan is
    identified by a number unique within the session.
    """

    protocol = fields.ReferenceField(ScanProtocol, required=True)
    """The scan acquisition protocol."""

    bolus_arrival_index = fields.IntField()
    """The bolus arrival volume index."""

    rois = fields.ListField(fields.EmbeddedDocumentField(Region))
    """The image regions of interest. There is one ROI per scan tumor."""

    registrations = fields.ListField(
        field=fields.EmbeddedDocumentField(Registration)
    )
    """
    The registrations performed on the scan.
    """

    def clean(self):
        """Verify that the bolus arrival index references a volume,."""
        arv = self.bolus_arrival_index
        if arv:
            if not self.volumes:
                raise ValidationError("Session does not have a volume")
            if arv < 0 or arv >= len(self.volumes):
                raise ValidationError(("Bolus arrival index does not refer"
                                       " to a valid volume index: %d") % arv)


class ModelingProtocol(mongoengine.Document):
    """The modeling procedure inputs."""

    meta = dict(collection='qiprofile_modeling_protocol')

    technique = fields.StringField(required=True)
    """
    The modeling algorithm or framework, e.g. ``Tofts``.
    """

    parameters = fields.DictField()
    """
    The modeling execution {*parameter*\ : *value*\ } dictionary, where
    *value* is a primitive or a dictionary, e.g.:

        {'r1': {'r1_0_val': 0.7, 'baseline_end_idx': 1}}
    """


class Modeling(Outcome):
    """
    The QIN pharmicokinetic modeling run on an image sequence.
    """

    class ParameterResult(mongoengine.EmbeddedDocument):
        """The output for a given modeling run result parameter."""

        filename = fields.StringField(required=True)
        """The voxel-wise mapping file path relative to the web app root."""

        average = fields.FloatField()
        """The average parameter value over all voxels."""

        label_map = fields.EmbeddedDocumentField(LabelMap)
        """The label map overlay NiFTI file."""

    class Source(mongoengine.EmbeddedDocument):
        """
        This Modeling.Source embedded class works around the following
        mongoengine limitation:

        * mongoengine does not allow heterogeneous collections, i.e.
          a domain model Document subclass can not have subclasses.
          Furthermore, the domain model Document class cannot be
          an inner class, e.g. ModelingProtocol.

        Consequently, the Modeling.source field cannot represent an
        abstract superclass of ScanProtocol and RegistrationProtocol.
        This Source embedded document introduces a disambiguation
        level by creating a disjunction object that can either hold
        a *scan reference or a *registration* reference.
        """

        scan = fields.ReferenceField(ScanProtocol)

        registration = fields.ReferenceField(RegistrationProtocol)

    protocol = fields.ReferenceField(ModelingProtocol, required=True)
    """The modeling protocol."""

    source = fields.EmbeddedDocumentField(Source, required=True)
    """
    The modeling source protocol.
    
    Since a given :class`Session` contains only one :class:`ImageSequence`
    per source protocol, the image sequence on which modeling is performed
    is determined by the source protocol. Specifying the source as a
    protocol rather than the specific scan or registration allows modeling
    to be embedded in the :class`Session` document rather than the
    :class:`SessionDetail`.
    """

    resource = fields.StringField(required=True)
    """The modeling imaging store resource name, e.g. ``pk_R3y9``."""

    result = fields.DictField(
        field=mongoengine.EmbeddedDocumentField(ParameterResult)
    )
    """
    The modeling {*parameter*: *result*} dictionary, where:

    - *parameter* is the lower-case underscore parameter key, e.g.
      ``k_trans``.

    - *result* is the corresponding :class:`ParameterResult`

    The parameters are determined by the :class:`ModelingProtocol`
    technique. For example, the `OHSU QIN modeling workflow`_ includes
    the following outputs for the FXL (`Tofts standard`_) model and the
    FXR (`shutter speed`_) model:

    - *fxl_k_trans*, *fxr_k_trans*: the |Ktrans| vascular permeability
       transfer constant

    - *delta_k_trans*: the FXR-FXL |Ktrans| difference

    - *fxl_v_e*, *fxr_v_e*: the |ve| extravascular extracellular volume
       fraction

    - *fxr_tau_i*: the |taui| intracellular |H2O| mean lifetime

    - *fxl_chi_sq*, *fxr_chi_sq*: the |chisq| intensity goodness of fit

    The REST client is responsible for anticipating and interpreting the
    meaning of the *parameter* based on the modeling technique. For
    example, if the image store has a session modeling resource
    ``pk_h7Jtl`` which includes the following files::

        k_trans.nii.gz
        k_trans_overlay.nii.gz
        chi_sq.nii.gz
        chi_sq_overlay.nii.gz

    then a REST database update client might calculate the average |Ktrans|
    and |chisq| values and populate the REST database as follows::

        t1 = ScanProtocol.get_or_create(scan_type='T1',
                                        defaults=dict(orientation='axial'))
        tofts = ModelingProtocol.get_or_create(technique='Tofts')
        ktrans_label_map = LabelMap(filename='k_trans_overlay.nii.gz',
                                    color_table='jet.txt')
        ktrans = Modeling.ParameterResult(filename='k_trans.nii.gz',
                                          average=k_trans_avg,
                                          label_map=ktrans_label_map)
        chisq_label_map = LabelMap(filename='k_trans_overlay.nii.gz',
                                   color_table='jet.txt')
        chisq = Modeling.ParameterResult(filename='chi_sq.nii.gz',
                                         average=chi_sq_avg,
                                         label_map=chisq_label_map)
        result = dict(ktrans=ktrans, chisq=chisq)
        session.modeling = Modeling(protocol=tofts, source=t1,
                                    resource='pk_h7Jtl', result=result)

    It is then the responsibility of an imaging web app REST read client
    to interpret the modeling result dictionary items and display them
    appropriately.

    .. reST substitutions:
    .. include:: <isogrk3.txt>
    .. |H2O| replace:: H\ :sub:`2`\ O
    .. |Ktrans| replace:: K\ :sup:`trans`
    .. |ve| replace:: v\ :sub:`e`
    .. |taui| replace:: |tau|\ :sub:`i`
    .. |chisq| replace:: |chi|\ :sup:`2`

    .. _OHSU QIN modeling workflow: http://qipipe.readthedocs.org/en/latest/api/pipeline.html#modeling
    .. _Tofts standard: http://onlinelibrary.wiley.com/doi/10.1002/(SICI)1522-2586(199909)10:3%3C223::AID-JMRI2%3E3.0.CO;2-S/abstract
    .. _shutter speed: http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2582583
    """

    def __str__(self):
        return "Modeling %s" % self.resource


class SessionDetail(mongoengine.Document):
    """The MR session detailed content."""

    meta = dict(collection='qiprofile_session_detail')

    scans = fields.ListField(field=mongoengine.EmbeddedDocumentField(Scan))
    """The list of scans."""


class Session(Encounter):
    """The MR session (a.k.a. *study* in DICOM terminology)."""

    modelings = fields.ListField(
        field=fields.EmbeddedDocumentField(Modeling)
    )
    """The modeling performed on the session."""

    tumor_extents = fields.ListField(
        field=fields.EmbeddedDocumentField(TumorExtent)
    )
    """The tumor extents measured from the scan."""

    detail = fields.ReferenceField(SessionDetail)
    """The session detail reference."""

    @classmethod
    def pre_delete(cls, sender, document, **kwargs):
        """Cascade delete this Session's detail."""

        if self.detail:
            self.detail.delete()

signals.pre_delete.connect(Session.pre_delete, sender=Session)
