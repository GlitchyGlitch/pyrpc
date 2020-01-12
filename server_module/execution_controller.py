from pyrpc.common.exceptions import (FunctionNotDefinedError, InternalServerError,
                                     WrongArgumentsError)

__all__ = ["ExecutionController"]


class ExecutionController():
    def __init__(self, function_list):
        self._function_list = function_list

    def call(self, name, args):
        try:
            returned_value = self._function_list[name](*args)
        except KeyError as _:
            raise FunctionNotDefinedError
        except TypeError as _:
            raise WrongArgumentsError
        except BaseException as _:
            raise InternalServerError
        return returned_value
