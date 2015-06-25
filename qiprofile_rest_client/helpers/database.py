"""Mongo Engine interaction utilities."""

def get_or_create(klass, pk, **non_pk):
    """
    This function stands in for the Mongo Engine ``get_or_create``
    collection method which was deprecated in mongoengine v0.8.0
    and dropped in mongoengine v0.10.0, since MongoDB does not
    support transactions.
    
    If there is an object of the given Mongo Engine data model
    class which matches the primary key, then that object is
    returned. Otherwise, a new object is created with the content
    prescribed by both the primary and non-primary parameters.
    
    The create step is an upsert, i.e. a new object is created only
    if it does not yet exist. The upsert allows for the small
    possibility that an object is created after the fetch attempt
    but before the create attempt. In that situation, the existing
    object non-key content is modified and the modified object is
    returned.
    
    :Note: The idiom used in this function modifies the solution
    proposed in http://stackoverflow.com/questions/25846462/mongoengine-replacing-get-or-create-with-upsert-update-one/25863633#25863633.
    That StackOverflow work-around returns the following error:
    
        ValueError: update only works with $ operators

    The work-around to the StackOverflow work-around is to use
    call *update* rather than *modify*.

    :param klass: the Mongo Engine data model class
    :param pk: the primary key {attribute: value} dictionary
    :param non_pk: the non-key {attribute: value} dictionary
    :return: the existing or new object
    """
    try:
        return klass.objects.get(**pk)
    except klass.DoesNotExist:
        mod_opts = {'set__' + attr: val for attr, val in non_pk.iteritems()}
        return klass.objects(**pk).update_one(upsert=True, **mod_opts)
