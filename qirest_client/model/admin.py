"""
The qiprofile administrative Mongodb data model.
"""

import mongoengine
from mongoengine import fields


class User(mongoengine.Document):
    """
    The application user.
    """

    meta = dict(collection='qiprofile_user')

    email = fields.StringField()
    first_time = fields.BooleanField(default=True)

    def __str__(self):
        return self.email


