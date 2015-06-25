from datetime import datetime
from mongoengine import (connect, ValidationError)
from mongoengine.connection import get_db
from nose.tools import (assert_true, assert_false, assert_equal, assert_raises)
from qiprofile_rest_client.model.subject import Subject
from qiprofile_rest_client.model.imaging import (
    Session, Scan, ScanProtocol, Registration, RegistrationProtocol, LabelMap,
    VoxelSize, SessionDetail, Volume, Point, Region, Modeling, ModelingProtocol
)
from qiprofile_rest_client.model.clinical import (
    Biopsy, Evaluation, Surgery, BreastSurgery, BreastPathology,
    SarcomaPathology, TNM, ModifiedBloomRichardsonGrade,
    HormoneReceptorStatus, FNCLCCGrade, NecrosisPercentValue,
    NecrosisPercentRange, necrosis_percent_as_score
)


class TestModel(object):
    """
    Basic data model test. A more complete test is found in the qiprofile_rest
    server TestSeed test suite.
    """
    def setup(self):
        connect(db='qiprofile_test')
 
    def test_subject(self):
        subject = Subject(project='QIN_Test', number=1)
        # The subject must have a collection.
        with assert_raises(ValidationError):
            subject.validate()

        subject.collection='Breast'
        subject.validate()

    def test_race(self):
        subject = Subject(project='QIN_Test', collection='Breast', number=1)
        subject.races = ['White', 'Black', 'Asian', 'AIAN', 'NHOPI']
        subject.validate()

        subject = Subject(project='QIN_Test', collection='Breast', number=1)
        subject.races = ['Invalid']
        with assert_raises(ValidationError):
            subject.validate()

        # Races must be a list.
        subject.races = 'White'
        with assert_raises(ValidationError):
            subject.validate()

    def test_ethnicity(self):
        subject = Subject(project='QIN_Test', collection='Breast', number=1)
        subject.ethnicity = 'Non-Hispanic'
        subject.validate()

        # The ethnicity is a controlled value.
        subject.ethnicity = 'Invalid'
        with assert_raises(ValidationError):
            subject.validate()

    def test_biopsy(self):
        subject = Subject(project='QIN_Test', collection='Breast', number=1)
        # The pathology.
        size = TNM.Size.parse('T3a')
        grade = ModifiedBloomRichardsonGrade(
            tubular_formation=2, nuclear_pleomorphism=1, mitotic_count=2
        )
        tnm = TNM(tumor_type='Breast', grade=grade, size=size,
                  metastasis=False, resection_boundaries=1,
                  lymphatic_vessel_invasion=False)
        estrogen=HormoneReceptorStatus(hormone='estrogen', positive=True,
                                       intensity=80)
        hormone_receptors = [estrogen]
        pathology = BreastPathology(tnm=tnm,
                                    hormone_receptors=hormone_receptors)
        # Add the encounter to the subject.
        date = datetime(2013, 1, 4)
        biopsy = Biopsy(date=date, weight=54, pathology=pathology)
        subject.encounters = [biopsy]
        # Validate the subject and embedded biopsy.
        subject.validate()

    def test_breast_surgery(self):
        subject = Subject(project='QIN_Test', collection='Breast', number=1)
        # The pathology.
        size = TNM.Size.parse('T2')
        grade = ModifiedBloomRichardsonGrade(
            tubular_formation=1, nuclear_pleomorphism=1, mitotic_count=1
        )
        tnm = TNM(tumor_type='Breast', grade=grade, size=size,
                  metastasis=False, resection_boundaries=1,
                  lymphatic_vessel_invasion=False)
        pathology = BreastPathology(tnm=tnm)
        # Add the encounter to the subject.
        date = datetime(2013, 1, 4)
        surgery = BreastSurgery(date=date, weight=54, surgery_type='Lumpectomy',
                               pathology=pathology)
        subject.encounters = [surgery]
        # Validate the subject and embedded surgery.
        subject.validate()

    def test_sarcoma_surgery(self):
        subject = Subject(project='QIN_Test', collection='Sarcoma', number=1)
        # The pathology.
        size = TNM.Size.parse('T3a')
        grade = FNCLCCGrade(
            differentiation=2, necrosis_score=1, mitotic_count=1
        )
        tnm = TNM(tumor_type='Sarcoma', grade=grade, size=size,
                  metastasis=False, resection_boundaries=1,
                  lymphatic_vessel_invasion=False)
        pathology = SarcomaPathology(tnm=tnm, location='Thigh')
        # Add the encounter to the subject.
        date = datetime(2014, 6, 19)
        surgery = Surgery(date=date, weight=47, pathology=pathology)
        subject.encounters = [surgery]
        # Validate the subject and embedded surgery.
        subject.validate()

    def test_tnm_size(self):
        for value in ['T1', 'Tx', 'cT4', 'T1b', 'cT2a']:
            size = TNM.Size.parse(value)
            assert_equal(str(size), value, "The TNM parse is incorrect -"
                                           " expected %s, found %s"
                                           % (value, str(size)))


    def test_necrosis_score(self):
        fixture = {
            0: dict(integer=0,
                    value=NecrosisPercentValue(value=0),
                    range=NecrosisPercentRange(
                        start=NecrosisPercentRange.LowerBound(value=0),
                        stop=NecrosisPercentRange.UpperBound(value=1))),
            1: dict(integer=40,
                    value=NecrosisPercentValue(value=40),
                    range=NecrosisPercentRange(
                        start=NecrosisPercentRange.LowerBound(value=40),
                        stop=NecrosisPercentRange.UpperBound(value=50))),
            2: dict(integer=50,
                    value=NecrosisPercentValue(value=50),
                    range=NecrosisPercentRange(
                        start=NecrosisPercentRange.LowerBound(value=50),
                        stop=NecrosisPercentRange.UpperBound(value=60)))
        }
        for expected, inputs in fixture.iteritems():
            for in_type, in_val in inputs.iteritems():
                actual = necrosis_percent_as_score(in_val)
                assert_equal(actual, expected,
                             "The necrosis score for %s is incorrect: %d" %
                             (in_val, expected))

    def test_treatment(self):
       # TODO - add the treatment test case.
       pass

    def test_session(self):
        # The session parent.
        subject = Subject(project='QIN_Test', collection='Breast', number=1)
        # The session.
        date = datetime(2013, 1, 4)
        session = Session(date=date)
        # Validate the subject and embedded session.
        subject.encounters = [session]
        subject.validate()


    def test_modeling(self):
        # The session subject.
        subject = Subject(project='QIN_Test', collection='Breast', number=1)
        # The modeling protocol must exist.
        mdl_pcl = self._get_or_create(ModelingProtocol,
                                      dict(technique='Bolero'),
                                      input_parameters=dict(r10_val=0.7))
        # The source protocol.
        scan_pcl = self._get_or_create(ScanProtocol, dict(scan_type='T1'))
        source = Modeling.Source(scan=scan_pcl)
        # The modeling data.
        ktrans = Modeling.ParameterResult(filename='/path/to/ktrans.nii.gz')
        modeling = Modeling(protocol=mdl_pcl, source=source, resource='pk_01',
                            result=dict(ktrans=ktrans))
        # Validate the subject and embedded session modeling.
        date = datetime(2014, 3, 1)
        session = Session(date=date, modelings=[modeling])
        subject.encounters = [session]
        subject.validate()

    def test_scan(self):
        # The scan protocol.
        voxel_size = VoxelSize(width=2, depth=4, spacing=2.4)
        protocol = self._get_or_create(ScanProtocol,
                                       dict(scan_type='T1'),
                                       orientation='axial',
                                       description='T1 AX SPIN ECHO',
                                       voxel_size=voxel_size)
        # The scan.
        scan = Scan(protocol=protocol, number=1)
        # Validate the session detail and embedded scan.
        detail = SessionDetail(scans=[scan])
        detail.validate()

    def test_bolus_arrival(self):
        # The scan protocol.
        protocol = self._get_or_create(ScanProtocol, dict(scan_type='T1'))
        # The scan with a bogus bolus arrival.
        scan = Scan(protocol=protocol, number=1, bolus_arrival_index=4)
        # The detail object.
        detail = SessionDetail(scans=[scan])
        # The bolus arrival index must refer to an existing volume.
        with assert_raises(ValidationError):
            detail.validate()

        # The scan volumes.
        vol_fmt = "volume%03d.nii.gz"
        create_volume = lambda number: Volume(filename=vol_fmt % number)
        scan.volumes = [create_volume(i + 1) for i in range(32)]
        # The bolus arrival is now valid.
        detail.validate()

        # The bolus arrival index must refer to a volume.
        scan.bolus_arrival_index = 32
        with assert_raises(ValidationError):
            detail.validate()

    def test_registration(self):
        # The scan protocol.
        scan_pcl = self._get_or_create(ScanProtocol, dict(scan_type='T1'))
        # The scan.
        scan = Scan(protocol=scan_pcl, number=1)

        # The registration protocol.
        reg_params = dict(transforms=['Rigid', 'Affine', 'SyN'])
        reg_pcl = self._get_or_create(RegistrationProtocol,
                                      dict(technique='ANTS'),
                                      parameters=reg_params)
        # The registration.
        reg = Registration(protocol=reg_pcl, resource='reg_h3Fk5')

        # Validate the session detail and embedded scan registration.
        scan.registrations = [reg]
        detail = SessionDetail(scans=[scan])
        detail.scans = [scan]
        detail.validate()

    def test_roi(self):
        # The scan protocol.
        scan_pcl = self._get_or_create(ScanProtocol, dict(scan_type='T1'))
        # The scan.
        scan = Scan(protocol=scan_pcl, number=1)

        # The ROI.
        mask = '/path/to/mask.nii.gz'
        label_map = LabelMap(filename='/path/to/label_map.nii.gz',
                             color_table='/path/to/color_table.nii.gz')
        centroid = Point(x=200, y=230, z=400)
        intensity = 31
        roi = Region(mask=mask, label_map=label_map, centroid=centroid,
                     average_intensity=intensity)

        # Validate the session detail and embedded scan ROI.
        scan.rois = [roi]
        detail = SessionDetail(scans=[scan])
        detail.scans = [scan]
        detail.validate()

    def _get_or_create(self, klass, pk, **opts):
        """
        :param klass: the data model class
        :param pk: the primary key {attribute: value} dictionary
        :param opts: the non-key {attribute: value} dictionary
        :return: the existing or new object
        """
        try:
            return klass.objects.get(**pk)
        except klass.DoesNotExist:
            opts.update(pk)
            obj = klass(**opts)
            obj.save()
            return obj

if __name__ == "__main__":
    import nose
    nose.main(defaultTest=__name__)
