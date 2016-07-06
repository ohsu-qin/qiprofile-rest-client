Model Development Notes
=======================

* mongoengine 0.8.7, and probably later versions, has the following
  bug:
  
  Each mongoengine non-embedded class embedded field must specify
  a class by reference rather than name, e.g.::
  
      volumes = fields.ListField(field=mongoengine.EmbeddedDocumentField(Image))
  
  rather than::

      # Don't do this!
      volumes = fields.ListField(field=mongoengine.EmbeddedDocumentField('Image'))

  If the class is referenced by name, then the model is initialized, but
  an attempt to save an object results in the following validation error::
  
      Invalid embedded document instance provided

  The recommended pattern is to define every class before it is referenced.

* MongoEngine does not 

* Validation errors are often highly misleading. For example, when a
  Subject data object is created with the following content::
      subject
        encounters: [
          surgery
            pathology
              tnm
                grade
                  necrosis_score: 3
        ]
  
  the *necrosis_score* violates the field choice constraint of 0, 1 or 2.
  The validation error message is as follows::

    ValidationError: ValidationError (Subject:None) (pathology.'Surgery' object has no attribute 'pk': ['encounters'])

  On the face of it, this message is worse than useless, since it suggests
  that the problem is with a Surgery object primary key. The technique
  for working from a validation error back to its cause is to examine
  the innermost class or reference attribute. In the above case,
  ``Subject``, ``pathology``, ``Surgery`` and ``encounters`` are mentioned.
  The innermost reference is the ``Surgery.pathology`` field, so start
  with the value referenced by that field. Visually validate the pathology
  object values, recursing down into the embedded objects, until the
  invalid data is discovered.
  
  This example highlights the importance of constraining the input to
  prevent data entry that violates a value constraint.
