"""
The qiprofile REST data model.

The model field choices are listed in the preferred display order,
most common to least common.

The data capture client has the following responsibility:

* Validate the data upon input as determined by the model
  validation documentation.

* Resolve conflicts between data capture and the model, e.g. the
  default value or validation.
"""
