import enum


class EntityPageException(Exception):
    pass


class EntityPageDynamicsBombed(EntityPageException):
    pass


class EntityPageNoData(EntityPageException):
    pass


class EntityPageDeAuth(EntityPageException):
    pass


EntityPageState = enum.Enum(
    'EntityPageState',
    (
            'initial',
#               |                                                       # NOQA
#               |                                                       # NOQA
            'pending',
#             /   \                                                     # NOQA
#            /     \                                                    # NOQA
       'failed', 'complete',
#                    |                                                  # NOQA
#                    |                                                  # NOQA
                 'inserted',
    )
)

EntityChunkState = enum.Enum(
    'EntityChunkState',
    (
           'incomplete',
#             /   \                                                     # NOQA
#            /     \                                                    # NOQA
        'spent', 'complete',
    )
)

