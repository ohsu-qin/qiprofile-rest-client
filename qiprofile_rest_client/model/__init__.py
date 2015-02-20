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

# Note: mongoengine 0.8.7 has the following bug:
# * Each mongoengine non-embedded class embedded field must specify
#   a class by reference rather than name, e.g.::
#   
#       class SessionDetail(mongoengine.Document):
#           volumes = fields.ListField(field=mongoengine.EmbeddedDocumentField(Volume))
#   
#   rather than::
# 
#       class SessionDetail(mongoengine.Document):
#           volumes = fields.ListField(field=mongoengine.EmbeddedDocumentField('Volume'))
# 
#   If the class is referenced by name, then the model is initialized, but
#   an attempt to save an object results in the following validation error::
#   
#       Invalid embedded document instance provided
