This history lists major release themes. See the GitHub commits
for change details.

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
