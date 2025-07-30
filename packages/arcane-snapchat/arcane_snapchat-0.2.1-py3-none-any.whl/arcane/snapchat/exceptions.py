class SnapchatAccountLostAccessException(Exception):
    """ Raised when we cannot access to an account """
    pass


class SnapchatAsyncReportNotReadyException(Exception):
    """ Raised when an async report is not ready yet"""
    pass
