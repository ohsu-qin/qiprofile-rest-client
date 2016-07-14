from datetime import datetime
from mongoengine import (connect, ValidationError)
from nose.tools import (assert_true, assert_false, assert_equal,
                        assert_almost_equal, assert_raises)
from qirest_client.helpers import database
from qirest_client.model.subject import (Project, ImagingCollection, Subject)
from qirest_client.model.common import TumorExtent
from qirest_client.model.imaging import (
    Session, Scan, ScanProtocol, Registration, RegistrationProtocol,
    MultiImageResource, SingleImageResource, LabelMap, SessionDetail,
    Image, Point, Region, Modeling, ModelingProtocol
)
from qirest_client.model.clinical import (
    Biopsy, Evaluation, Surgery, PathologyReport, TumorLocation,
    TNM, BreastSurgery, BreastPathology, ResidualCancerBurden,
    ModifiedBloomRichardsonGrade, HormoneReceptorStatus,
    SarcomaPathology, FNCLCCGrade, NecrosisPercentValue,
    NecrosisPercentRange, necrosis_percent_as_score
)


class TestModel(object):
    """
    Basic data model test. A more complete test is found in the qirest
    server TestSeed test suite.
    """
    def setup(self):
        self._connection = connect(db='qiprofile_test')
        self._connection.drop_database('qiprofile_test')

    def tearDown(self):
        self._connection.drop_database('qiprofile_test')

    def test_project(self):
        prj = Project()
        # The project must have a name.
        with assert_raises(ValidationError):
            prj.validate()
        prj.name = 'Breast'
        prj.validate()

    def test_collection(self):
        # The collection must have a name.
        with assert_raises(ValidationError):
            ImagingCollection(project='QIN_Test').validate()
        # The collection must have a project.
        with assert_raises(ValidationError):
            ImagingCollection(name='Breast').validate()
        # A valid collection.
        coll = ImagingCollection(project='QIN_Test', name='Breast')
        coll.validate()

    def test_subject(self):
        subject = Subject()
        # The collection must have a project.
        with assert_raises(ValidationError):
            subject.validate()
        subject.project = 'QIN_Test'
        # The collection must have a number.
        with assert_raises(ValidationError):
            subject.validate()
        subject.number = 1
        # The subject must have a collection.
        with assert_raises(ValidationError):
            subject.validate()
        subject.collection = 'Breast'
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
    
    def test_breast_biopsy(self):
        """
        This Breast biopsy test case is a variation of the Breast
        surgery test case. Notably, this test case exercises multiple
        tumors. There is no Sarcoma biopsy test case.
        """
        subject = Subject(project='QIN_Test', collection='Breast', number=1)
        # The pathology.
        size = TNM.Size.parse('T3a')
        size.validate()
        grade = ModifiedBloomRichardsonGrade(
            tubular_formation=2, nuclear_pleomorphism=1, mitotic_count=2
        )
        grade.validate()
        tnm = TNM(tumor_type='Breast', grade=grade, size=size,
                  metastasis=False, resection_boundaries=1,
                  lymphatic_vessel_invasion=False)
        tnm.validate()
        estrogen1 = HormoneReceptorStatus(hormone='estrogen', positive=True,
                                          intensity=80)
        estrogen1.validate()
        hormone_receptors1 = [estrogen1]
        extent1 = TumorExtent(length=48, width=31, depth=19)
        extent1.validate()
        tumor1_pathology = BreastPathology(tnm=tnm, extent=extent1,
                                           hormone_receptors=hormone_receptors1)
        tumor1_pathology.validate()
        estrogen2 = HormoneReceptorStatus(hormone='estrogen', positive=False)
        estrogen2.validate()
        hormone_receptors2 = [estrogen2]
        extent2 = TumorExtent(length=27, width=16, depth=8)
        extent2.validate()
        tumor2_pathology = BreastPathology(extent=extent2,
                                           hormone_receptors=hormone_receptors2)
        tumor2_pathology.validate()
        # The pathology aggregate.
        pathology = PathologyReport(tumors=[tumor1_pathology, tumor2_pathology])
        pathology.validate()
        # Add the encounter to the subject.
        date = datetime(2013, 1, 4)
        biopsy = Biopsy(date=date, weight=54, pathology=pathology)
        biopsy.validate()
        subject.encounters = [biopsy]
        subject.validate()

    def test_rcb_index(self):
        extent = TumorExtent(length=32, width=12)
        rcb = ResidualCancerBurden(
                tumor_cell_density=40,
                dcis_cell_density=10,
                positive_node_count=6,
                largest_nodal_metastasis_length=8
            )
        path = BreastPathology(extent=extent, rcb=rcb)
        rcb_index = path.rcb_index()
        assert_almost_equal(rcb_index, 3.695, 3,
                            msg="The RCB index is incorrect: %f" % rcb_index)

    def test_rcb_class(self):
        path = BreastPathology()
        for expected, rcb_index in enumerate((0, 1.2, 1.4, 3.5)):
            actual = path.rcb_class(rcb_index)
            assert_equal(actual, expected,
                         "The RCB class of RCB index %f is incorrect: %d" % 
                        (rcb_index, actual))

    def test_breast_surgery(self):
        subject = Subject(project='QIN_Test', collection='Breast', number=1)

        # The pathology report.
        size = TNM.Size.parse('T2')
        size.validate()
        grade = ModifiedBloomRichardsonGrade(
            tubular_formation=1, nuclear_pleomorphism=1, mitotic_count=1
        )
        grade.validate()
        tnm = TNM(tumor_type='Breast', grade=grade, size=size,
                  metastasis=False, resection_boundaries=1,
                  lymphatic_vessel_invasion=False)
        tnm.validate()
        location = TumorLocation(sagittal_location='Left')
        location.validate()
        tumor_pathology = BreastPathology(tnm=tnm, location=location)
        tumor_pathology.validate()
        pathology = PathologyReport(tumors=[tumor_pathology])
        pathology.validate()

        # Add the encounter to the subject.
        date = datetime(2013, 1, 4)
        surgery = BreastSurgery(date=date, weight=54, surgery_type='Lumpectomy',
                               pathology=pathology)
        surgery.validate()
        subject.encounters = [surgery]
        subject.validate()
    
    def test_sarcoma_surgery(self):
        subject = Subject(project='QIN_Test', collection='Sarcoma', number=1)
        
        # The pathology report.
        size = TNM.Size.parse('T3a')
        size.validate()
        grade = FNCLCCGrade(
            differentiation=2, necrosis_score=1, mitotic_count=1
        )
        grade.validate()
        tnm = TNM(tumor_type='Sarcoma', grade=grade, size=size,
                  metastasis=False, resection_boundaries=1,
                  lymphatic_vessel_invasion=False)
        tnm.validate()
        location = TumorLocation(body_part='Thigh', sagittal_location='Left',
                                 coronal_location='Posterior')
        location.validate()
        tumor_pathology = SarcomaPathology(tnm=tnm, location=location)
        tumor_pathology.validate()
        pathology = PathologyReport(tumors=[tumor_pathology])
        pathology.validate()

        # Add the encounter to the subject.
        date = datetime(2014, 6, 19)
        surgery = Surgery(date=date, weight=47, pathology=pathology)
        surgery.validate()
        subject.encounters = [surgery]
        subject.validate()
    
    def test_tnm_size(self):
        for value in ['T1', 'Tx', 'cT4', 'T1b', 'cT2a']:
            size = TNM.Size.parse(value)
            size.validate()
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
        # The test subject.
        subject = Subject(project='QIN_Test', collection='Breast', number=1)
        # The test session.
        date = datetime(2013, 1, 4)
        session = Session(date=date)
        session.validate()
        subject.encounters = [session]
        subject.validate()
    
    def test_add_encounter(self):
        # The test subject.
        subject = Subject(project='QIN_Test', collection='Breast', number=1)
        # Add the test encounters.
        encounters = [Biopsy(date=datetime(2014, m, 1)) for m in (3, 5, 7)]
        subject.add_encounter(encounters[1])
        assert_equal(subject.encounters, encounters[1:2])
        subject.add_encounter(encounters[0])
        assert_equal(subject.encounters, encounters[0:2])
        subject.add_encounter(encounters[2])
        assert_equal(subject.encounters, encounters)
    
    def test_scan(self):
        # The scan protocol.
        protocol = database.get_or_create(ScanProtocol, dict(technique='T1'))
        # The scan.
        scan = Scan(protocol=protocol, number=1)
        scan.validate()
        # Validate the session detail embedded scan.
        detail = SessionDetail(scans=[scan])
        detail.validate()
    
    def test_registration(self):
        # The scan protocol.
        scan_pcl = database.get_or_create(ScanProtocol, dict(technique='T1'))
        # The scan.
        scan = Scan(protocol=scan_pcl, number=1)
        scan.validate()
        # The registration protocol.
        reg_pcl = database.get_or_create(RegistrationProtocol,
                                         dict(technique='FLIRT'))
        # The registration volumes.
        vol_imgs = [Image(name="volume00%s.nii.gz" % vol) for vol in range(1, 4)]
        volumes = MultiImageResource(name='reg', images=vol_imgs)
        # The registration time series.
        time_series_img = Image(name='reg_ts.nii.gz')
        time_series = SingleImageResource(name='reg_ts', image=time_series_img)
        reg = Registration(protocol=reg_pcl, volumes=volumes, time_series=time_series)
        reg.validate()
    
        # Validate the session detail and embedded scan registration.
        scan.registrations = [reg]
        detail = SessionDetail(scans=[scan])
        detail.scans = [scan]
        detail.validate()
    
    def test_roi(self):
        # The scan protocol.
        scan_pcl = database.get_or_create(ScanProtocol,
                                          dict(technique='T1'))
        # The scan.
        scan = Scan(protocol=scan_pcl, number=1)
        scan.validate()
    
        # The ROI.
        centroid = Point(x=200, y=230, z=400)
        intensity = 31
        metadata = dict(centroid=centroid, average_intensity=intensity)
        mask = Image(name='lesion1.nii.gz', metadata=metadata)
        label_map = LabelMap(name='lesion1_color.nii.gz',
                             color_table='color_table.nii.gz')
        label_map.validate()
        roi = Region(mask=mask, resource='roi', label_map=label_map, centroid=centroid)
        roi.validate()
        
        # Validate the session detail and embedded scan ROI.
        scan.rois = [roi]
        detail = SessionDetail(scans=[scan])
        detail.scans = [scan]
        detail.validate()
    
    def test_modeling_protocol(self):
        # The modeling protocol content.
        cfg = {'Fastfit': {'model_name': 'fxr.model'},
               'R1': {'r1_0_val': 0.7, 'baseline_end_idx': 1}}
        mdl_pcl_key = dict(technique='BOLERO', configuration=cfg)
        mdl_pcl = database.get_or_create(ModelingProtocol, mdl_pcl_key)
        assert_equal(mdl_pcl.configuration, cfg,
                     "The fetched modeling configuration is incorrect: %s" %
                     mdl_pcl.configuration)

    def test_modeling(self):
        # The test subject.
        subject = Subject(project='QIN_Test', collection='Breast', number=1)
        # The modeling protocol.
        cfg = {'Fastfit': {'model_name': 'fxr.model'},
               'R1': {'r1_0_val': 0.7, 'baseline_end_idx': 1}}
        mdl_pcl_key = dict(technique='BOLERO', configuration=cfg)
        mdl_pcl = database.get_or_create(ModelingProtocol, mdl_pcl_key)
        # The source protocol.
        scan_pcl = database.get_or_create(ScanProtocol, dict(technique='T1'))
        source = Modeling.Source(scan=scan_pcl)
        # The modeling data.
        ktrans_img = Image(name='ktrans.nii.gz')
        ktrans = Modeling.ParameterResult(image=ktrans_img)
        modeling = Modeling(protocol=mdl_pcl, source=source, resource='pk_01',
                            result=dict(ktrans=ktrans))
        modeling.validate()
        # Validate the subject embedded session modeling.
        date = datetime(2014, 3, 1)
        session = Session(date=date, modelings=[modeling])
        session.validate()
        subject.encounters = [session]
        subject.validate()

if __name__ == "__main__":
    import nose
    nose.main(defaultTest=__name__)
