class PublicError(Exception):
    """
    This exception should not convey any sensitive information, as its message will almost always be displayed to the
    user.
    """
