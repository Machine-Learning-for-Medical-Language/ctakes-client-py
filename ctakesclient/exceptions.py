"""Error types"""


class CtakesError(Exception):
    """
    Package level error
    """
    pass


class ClientError(CtakesError):
    """
    HTTP request/response problem with server
    """
    pass


class TypeSystemError(CtakesError):
    """
    Ctakes Type System, specific to cTAKES REST and cNLP transformer APIs
    """
    pass


class FileError(CtakesError):
    """
    File problems reading/writing/serializing
    """
    pass


class BSVError(FileError):
    """
    Bar|Separated|Values error
    """
    pass
