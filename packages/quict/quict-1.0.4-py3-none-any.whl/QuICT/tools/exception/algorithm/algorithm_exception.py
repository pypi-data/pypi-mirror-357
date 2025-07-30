from QuICT.tools.exception import QuICTException


class GetBeforeRunError(QuICTException):
    """ Try to get a property that will be set only after the algorithm has run. """
    def __init__(self, msg: str = None):
        super().__init__(3501, msg)
