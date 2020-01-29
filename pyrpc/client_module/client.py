import socket

from pyrpc.common.exceptions import (BadPDUFormatError,
                                     FunctionNotDefinedError,
                                     InternalServerError, MessageTooLongError,
                                     WrongArgumentsError, PDUFieldNotExistsError)
from pyrpc.common.types import ProtocolDataUnit

# FIXME: dir calls ___getaddr__ > s.sendall() while s = None

__all__ = ["Client"]


class Client():
    ERROR_TABLE = [InternalServerError, FunctionNotDefinedError,
                   WrongArgumentsError, MessageTooLongError, BadPDUFormatError]

    def __init__(self, ip="127.0.0.1", port=3672):
        self._s = None
        self._address = (ip, port)

    def connect(self):
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect(self._address)

    def close(self):
        self._s.shutdown(socket.SHUT_RDWR)
        self._s.close()

    def __getattr__(self, name):

        def function(*args):
            pdu_out = ProtocolDataUnit()
            pdu_out.set_request(name, list(args))
            self._s.sendall(pdu_out.dumps())
            try:
                raw_data = self._s.recv(ProtocolDataUnit.MAX_LENGTH)
                pdu_in = ProtocolDataUnit(raw_data)
                try:
                    raise Client.ERROR_TABLE[pdu_in.error]
                except PDUFieldNotExistsError as _:
                    pass
                return pdu_in.func_returned
            except socket.timeout as _:
                pass

        return function
