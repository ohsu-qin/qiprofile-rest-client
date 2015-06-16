Unit testing notes
==================

* mongoengine 0.8.7 has the following bug:
  
  Each mongoengine non-embedded class embedded field must specify
  a class by reference rather than name, e.g.::
  
      class SessionDetail(mongoengine.Document):
          volumes = fields.ListField(field=mongoengine.EmbeddedDocumentField(Volume))
  
  rather than::

      class SessionDetail(mongoengine.Document):
          volumes = fields.ListField(field=mongoengine.EmbeddedDocumentField('Volume'))

  If the class is referenced by name, then the model is initialized, but
  an attempt to save an object results in the following validation error::
  
      Invalid embedded document instance provided
