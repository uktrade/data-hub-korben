class Client:
    '''
    CRUD functions for single objects that either (in the case of read) call
    sync and ETL code to bring in fresh CDMS data or (in the case of write)
    call “reverse ETL” code to send data to CDMS.

    Functions here run through required CDMS operations and then (in the case
    of success) call Django methods.
    '''

    def create(model_instance):
        '''
        Create and sync a model instance in both CDMS and Django database, return
        it. Uses traversal to sync any children created.
        '''
        raise NotImplementedError()

    def read(Model, guid, prefetch=None):
        '''
        Sync (including ETL run for single object) and return the Django
        representation of a model. Optionally frefetch related objects (using
        traversal code).
        '''
        raise NotImplementedError()

    def update(model_instance):
        'Write changes in a model instance to both CDMS and Django'
        raise NotImplementedError()

    def delete(model_instance):
        '''
        Delete an instance from both CDMS and Django database, handle child
        deletion.
        '''
        raise NotImplementedError()
