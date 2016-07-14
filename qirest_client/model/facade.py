"""This facade helper module provides a qiprofile REST facade."""

import os
import re
from qiutil.logging import logger
from .model.subject import Subject
from .model.imaging import (Session, Modeling)

SBJ_REGEX = re.compile('^(\w+?)(\d+)$')

SESS_REGEX = re.compile('^Session(\d+)$')


def find_subject(project, subject, create=False):
    """
    Finds the given qiprofile subject. If it doesn't exists
    and the *create* flag is set, then the subject is created.

    :param project: the project name
    :param subject: the subject name
    :param create: flag indicating whether to create the subject
    :return: the Subject instance, or None if not found
    """
    # The collection name and subject number.
    collection, sbj_nbr_str = SBJ_REGEX.match(subject).groups()
    sbj_nbr = int(sbj_nbr_str)

    # Fetch the subject.
    try:
        sbj = Subject.objects.get(project__name=project,
                                  collection__name=collection,
                                  number=sbj_nbr)
    except Subject.DoesNotExist:
        if create:
            sbj = Subject(project=project, collection=collection, number=sbj_nbr)
            sbj.save()
        else:
            return

    return sbj


def find_session(project, subject, session, create=False):
    """
    Finds the given qiprofile subject. If it doesn't exists
    and the *create* flag is set, then the session is created.

    :param project: the project name
    :param subject: the subject name
    :param session: the session name
    :param create: flag indicating whether to create the subject
    :return: the Session instance, or None if not found
    """
    # The session number.
    sess_nbr_str = SESS_REGEX.match(session).group(1)
    sess_nbr = int(sess_nbr_str)

    # Fetch the subject.
    sbj = find_subject(project, subject, create)
    if not sbj:
        return
    try:
        sess = Session.objects.get(subject=sbj, number=sess_nbr)
    except Subject.DoesNotExist:
        if create:
            sess = Session(subject=subject, number=sess_nbr)
            sess.save()
        else:
            return

    return sess


def save_subject(project, subject, **opts):
    """
    Creates the qiprofile subject, if necessary, and updates
    the given subject fields.

    :param project: the project name
    :param subject: the subject name
    :param opts: the ``qiprofile.models.Subject`` non-identifier
        field name-value parameters
    :return: the Subject instance
    """
    # The qiprofile collection and subject number.
    collection, sbj_nbr_str = SBJ_REGEX.match(subject).groups()
    sbj_nbr = int(sbj_nbr_str)

    # Make the subject.
    sbj = Subject(project=project, collection=collection, number=sbj_nbr)
    for attr, value in opts.iteritems():
        setattr(sbj, attr, value)

    # Save the subject.
    logger(__name__).debug("Saving %s Subject %s..." % (project, subject))
    sbj.save()
    logger(__name__).debug("Saved %s Subject %s." % (project, subject))


def save_session(project, subject, session, **opts):
    """
    :param project: the project name
    :param subject: the subject name
    :param session: the session name
    :param opts: the ``qiprofile.models.Session`` non-identifier field
        name-value parameters
    :return: the Session instance
    """
    # The session number.
    sess_nbr_str = SESS_REGEX.match(session).group(1)
    sess_nbr = int(sess_nbr_str)

    # The subject.
    sbj = find_subject(project, subject, create=True)

    # Make the session.
    sess = Session(subject=sbj, number=sess_nbr, **opts)

    # Save the session.
    logger(__name__).debug("Saving %s Subject %s Session %s..." %
                           (project, subject, session))
    sess.save()
    logger(__name__).debug("Saved %s Subject %s Session %s." %
                           (project, subject, session))


def save_modeling(project, subject, session, assessor, **opts):
    """
    :param project: the project id
    :param subject: the subject name
    :param session: the session name
    :param assessor: the XNAT assessor name
    :param opts: the ``qiprofile.models.Modeling`` non-identifier field
        name-value parameters
    :return: the Modeling instance
    """
    # The session.
    sess = find_session(project, subject, session, create=True)

    # The modeling object.
    mdl = Modeling(session=sess, name=assessor, **opts)
    mdl.save()
