from nose.tools import (assert_true, assert_false, assert_equal, assert_raises)
from datetime import datetime
import pytz
from mongoengine import (connect, ValidationError)
from mongoengine.connection import get_db
from qiprofile_rest_client.model.subject import Subject
from qiprofile_rest_client.model.imaging import (
  Session, Scan, ScanProtocol, Registration, RegistrationProtocol, LabelMap,
  VoxelSize, SessionDetail, Volume, Point, Region, Modeling, ModelingProtocol)
from qiprofile_rest_client.model.clinical import (Encounter, Evaluation, TNM)

class TestModel(object):
    """
    Basic data model test. A more complete test is found in the qiprofile_rest
    server TestSeed test suite.
    """
    def setup(self):
        connect(db='qiprofile_test')
        self.db = get_db()
        self.db.connection.drop_database('qiprofile_test')
    
    def tearDown(self):
      self.db.connection.drop_database('qiprofile_test')

    def test_subject(self):
        subject = Subject(project='QIN_Test', number=1)
        # The subject must have a collection.
        with assert_raises(ValidationError):
            subject.save()
        
        subject.collection='Breast'
        subject.save()

    def test_race(self):
        subject = Subject(project='QIN_Test', collection='Breast', number=1)
        subject.races = ['White', 'Black', 'Asian', 'AIAN', 'NHOPI']
        subject.save()

        subject = Subject(project='QIN_Test', collection='Breast', number=1)
        subject.races = ['Invalid']
        with assert_raises(ValidationError):
            subject.save()

        # Races must be a list.
        subject.races = 'White'
        with assert_raises(ValidationError):
            subject.save()

    def test_ethnicity(self):
        subject = Subject(project='QIN_Test', collection='Breast', number=1)
        subject.ethnicity = 'Non-Hispanic'
        subject.save()

        # The ethnicity is a controlled value.
        subject.ethnicity = 'Invalid'
        with assert_raises(ValidationError):
            subject.save()

    def test_encounter(self):
        subject = Subject(project='QIN_Test', collection='Breast', number=1)
        date = datetime(2013, 1, 4, tzinfo=pytz.utc)
        encounter = Encounter(encounter_type='Biopsy', date=date)
        subject.encounters = [encounter]
        # The encounter outcome is optional.
        subject.save()

        # Add the evaluation.
        evaluation = Evaluation()
        outcome = TNM()
        evaluation.outcomes = [outcome]
        encounter.evaluation = evaluation
        # Save the subject and embedded encounter.
        subject.save()

    def test_tnm_size(self):
        for value in ['T1', 'Tx', 'cT4', 'T1b', 'cT2a']:
            size = TNM.Size.parse(value)
            assert_equal(str(size), value, "The TNM parse is incorrect -"
                                           " expected %s, found %s"
                                           % (value, str(size)))

    def test_session(self):
        # The session parent.
        subject = Subject(project='QIN_Test', collection='Breast', number=1)
        # The session.
        date = datetime(2013, 1, 4, tzinfo=pytz.utc)
        session = Session(acquisition_date=date)

        # Save the subject and embedded session.
        subject.sessions = [session]
        subject.save()

    def test_modeling(self):
        # The session subject.
        subject = Subject(project='QIN_Test', collection='Breast', number=1)
        
        # The modeling protocol.
        pcl_defs = dict(input_parameters=dict(r10_val=0.7))
        protocol, _ = ModelingProtocol.objects.get_or_create(
            technique='Bolero', defaults=pcl_defs
        )
        
        # The source protocol.
        scan_pcl, _ = ScanProtocol.objects.get_or_create(scan_type='T1')
        source = Modeling.Source(scan=scan_pcl)
        
        # The modeling data.
        ktrans = Modeling.ParameterResult(filename='/path/to/ktrans.nii.gz')
        result = dict(ktrans=ktrans)
        modeling = Modeling(protocol=protocol, source=source, resource='pk_01',
                       result=result)

        # Save the subject and embedded session modeling.
        date = datetime(2014, 3, 1, tzinfo=pytz.utc)
        session = Session(acquisition_date=date, modelings=[modeling])
        subject.sessions = [session]
        subject.save()

    def test_scan(self):
        # The scan protocol.
        voxel_size = VoxelSize(width=2, depth=4, spacing=2.4)
        pcl_defs = dict(scan_type='T1', orientation='axial',
                        description='T1 AX SPIN ECHO', voxel_size=voxel_size)
        protocol, _ = ScanProtocol.objects.get_or_create(scan_type='T1',
                                                         defaults=pcl_defs)
        # The scan.
        scan = Scan(protocol=protocol, number=1)

        # Save the session detail and embedded scan.
        detail = SessionDetail(scans=[scan])
        detail.save()

    def test_bolus_arrival(self):
        # The scan protocol.
        protocol, _ = ScanProtocol.objects.get_or_create(scan_type='T1')
        # The scan with a bogus bolus arrival.
        scan = Scan(protocol=protocol, number=1, bolus_arrival_index=4)
        # The detail object.
        detail = SessionDetail(scans=[scan])
        # The bolus arrival index must refer to an existing volume.
        with assert_raises(ValidationError):
            detail.save()
        
        # The scan volumes.
        create_volume = lambda number: Volume(filename="volume%03d.nii.gz" % number)
        scan.volumes = [create_volume(i + 1) for i in range(32)]
        # The bolus arrival is now valid.
        detail.save()

        # The bolus arrival index must refer to a volume.
        scan.bolus_arrival_index = 32
        with assert_raises(ValidationError):
            detail.save()

    def test_registration(self):
        # The scan protocol.
        scan_pcl, _ = ScanProtocol.objects.get_or_create(scan_type='T1')
        # The scan.
        scan = Scan(protocol=scan_pcl, number=1)

        # The registration protocol.
        reg_params = dict(transforms=['Rigid', 'Affine', 'SyN'])
        reg_pcl_defs = dict(parameters=reg_params)
        reg_pcl, _ = RegistrationProtocol.objects.get_or_create(
            technique='ANTS',defaults=reg_pcl_defs
        )
        # The registration.
        reg = Registration(protocol=reg_pcl, resource='reg_h3Fk5')
        
        # Save the session detail and embedded scan registration.
        scan.registrations = [reg]
        detail = SessionDetail(scans=[scan])
        detail.scans = [scan]
        detail.save()

    def test_roi(self):
        # The scan protocol.
        protocol, _ = ScanProtocol.objects.get_or_create(scan_type='T1')
        # The scan.
        scan = Scan(protocol=protocol, number=1)

        # The ROI.
        mask = '/path/to/mask.nii.gz'
        label_map = LabelMap(filename='/path/to/label_map.nii.gz',
                             color_table='/path/to/color_table.nii.gz')
        centroid = Point(x=200, y=230, z=400)
        intensity = 31
        roi = Region(mask=mask, label_map=label_map, centroid=centroid,
                     average_intensity=intensity)

        # Save the session detail and embedded scan ROI.
        scan.rois = [roi]
        detail = SessionDetail(scans=[scan])
        detail.scans = [scan]
        detail.save()

if __name__ == "__main__":
    import nose
    nose.main(defaultTest=__name__)
