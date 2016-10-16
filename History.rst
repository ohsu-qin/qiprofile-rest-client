This history lists major release themes. See the GitHub commits
for change details.

6.2.2 / 2016-10-16
------------------
* Add diagnosis date.

6.2.1 / 2016-07-14
------------------
* Add Project.

6.1.2 / 2016-07-06
------------------
* Rename from qiprofile-rest-client to qirest-client.

6.1.1 / 2016-07-06
------------------
* Replace TimeSeries and Volumes by resources.

5.12.1 / 2016-03-18
-------------------
* Make TimeSeries and Volumes Resource subclasses.

5.11.5 / 2016-03-03
-------------------
* Replace corrupted PyPI release.

5.11.4 / 2016-03-03
-------------------
* Relax the requirement versions.

5.11.3 / 2016-02-22
-------------------
* ImagingCollection requires a project.

5.11.2 / 2016-02-22
-------------------
* ImagingCollection url is a string.

5.11.1 / 2016-02-22
-------------------
* Add the ImagingCollection.

5.10.1 / 2016-02-03
-------------------
* Every protocol has a technique and configuration.

5.9.1 / 2015-12-23
------------------
* Change file_name field to name.

5.8.1 / 2015-12-03
------------------
* The ModelingProtocol consists of the configuration field.

5.7.2 / 2015-11-04
------------------
* Update the model doc.

5.7.1 / 2015-11-04
------------------
* Generalize the modeling protocol parameters.

5.6.3 / 2015-09-09
------------------
* Qualify tumor location.

5.6.2 / 2015-08-02
------------------
Add RCB to BreastPathology.

5.6.1 / 2015-07-28
------------------
Separate pathology into tumors.

5.5.4 / 2015-06-30
------------------
Fix Subject.add_encounter.

5.5.3 / 2015-06-26
------------------
Add Subject.add_encounter method.

5.5.2 / 2015-06-25
------------------
Add get_or_create utility.

5.5.1 / 2015-06-25
------------------
Upgrade to MongoDB 3.

5.4.5 / 2015-06-23
------------------
Expand the breast surgery type and subject gender CVs.

5.4.4 / 2015-06-19
------------------
Allow a KI67 value of zero.

5.4.3 / 2015-06-18
------------------
* Dosage amount is a cumulative normalized float.
* Rename Sarcoma grade necrosis to necrosis_score.

5.4.2 / 2015-06-15
------------------
* Rename Radiation and BreastSurgery fields.

5.4.1 / 2015-06-09
------------------
* Session is an encounter.

5.3.1 / 2015-06-03
------------------
* Move weight from session to encounter.

5.2.2 / 2015-05-26
------------------
* Rename necrosis_pct field to necrosis_percent.

5.2.1 / 2015-05-22
------------------
* Change Treatment begin_date to start_date and Dosage days
  to duration.

5.1.4 / 2015-03-07
------------------
* The Grade composite score is a computed virtual property.

5.1.3 / 2015-03-07
------------------
* Move subject weight from Subject to Session.

5.1.2 / 2015-03-03
------------------
* Session number is obsolete, acquisition date is required.

5.1.1 / 2015-02-20
------------------
* Split out from qiprofile-rest.
