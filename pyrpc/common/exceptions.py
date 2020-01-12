__all__ = ["InternalServerError", "MessageTooLongError",
           "FunctionNotDefinedError", "WrongArgumentsError",
           "PDUFieldNotExistsError", "BadPDUFormatError"]


class InternalServerError(Exception):
    pass


class MessageTooLongError(Exception):
    pass


class FunctionNotDefinedError(Exception):
    pass


class WrongArgumentsError(Exception):
    pass


class PDUFieldNotExistsError(Exception):
    pass


class BadPDUFormatError(Exception):
    pass
