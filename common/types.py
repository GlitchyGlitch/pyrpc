import json

from pyrpc.common.exceptions import (BadPDUFormatError, MessageTooLongError,
                                     PDUFieldNotExistsError)

__all__ = ["ProtocolDataUnit"]


class ProtocolDataUnit():
    '''
    To obejct can be passed raw_data or value. If both are passed, value is ignored.
    '''
    MAX_LENGTH = 2048

    def __init__(self, raw_data=bytes(), value=None):
        try:
            if raw_data:
                self.loads(raw_data)
            elif value:
                self.set(**value)
        except AttributeError as _:
            raise BadPDUFormatError

    def set(self, value):
        if not isinstance(value, dict):
            raise BadPDUFormatError
        self.__dict__ = value

    def get(self):
        return self.__dict__.copy()

    def loads(self, raw_data):
        if not isinstance(raw_data, bytes):
            raise BadPDUFormatError
        if len(raw_data) > ProtocolDataUnit.MAX_LENGTH:
            raise MessageTooLongError
        try:
            value = json.loads(raw_data.decode("utf-8"))
        except json.decoder.JSONDecodeError:
            raise BadPDUFormatError
        self.set(value)

    def dumps(self):
        raw_data = json.dumps(self.get())
        return bytes(raw_data.encode("utf-8"))

    def set_request(self, function_name, function_args):
        if (not isinstance(function_name, str)) or (not isinstance(function_args, list)):
            raise BadPDUFormatError
        self.__dict__.clear()
        self.func_name = function_name
        self.func_args = function_args

    def set_response(self, returned_value):
        self.__dict__.clear()
        self.func_returned = returned_value

    def set_exception(self, error_code):
        """
        |-----------------------------------|
        | 00 | InternalServerError          |
        |-----------------------------------|
        | 01 | FunctionNotDefinedError      |
        |-----------------------------------|
        | 02 | WrongArgumentsError          |
        |-----------------------------------|
        | 03 | MessageTooLongError          |
        |-----------------------------------|
        | 04 | PDUFieldNotExistsError       |
        |-----------------------------------|
        | 05 | BadPDUFormatError            |
        |-----------------------------------|

        """
        if not isinstance(error_code, int):
            raise BadPDUFormatError
        self.error = error_code

    def __getattr__(self, name):
        try:
            return self.get()[name]
        except KeyError as _:
            raise PDUFieldNotExistsError
