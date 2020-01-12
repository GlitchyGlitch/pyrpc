import socket
from threading import Event, Lock, Thread

from pyrpc.common.exceptions import (FunctionNotDefinedError,
                                     InternalServerError, PDUFieldNotExistsError,
                                     WrongArgumentsError, MessageTooLongError,
                                     BadPDUFormatError)
from pyrpc.common.types import ProtocolDataUnit
from pyrpc.server_module.execution_controller import ExecutionController

__all__ = ["Server"]


class Server():
    def __init__(self, ip="0.0.0.0", port=3672):
        self._s = None
        self._address = (ip, port)
        self._global_stop_event = Event()
        self._lock = Lock()
        self._exec_controller = None
        self._function_list = {}

    def start(self):
        self._exec_controller = ExecutionController(self._function_list)
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.bind(self._address)
        self._s.listen(32)
        while not self._global_stop_event.is_set():
            client, address = self._s.accept()
            connection = Connection(
                client,
                address,
                self._exec_controller,
                self._global_stop_event,
                self._lock,
            )
            connection.start()
        self._stop()

    def add_function(self, reference):
        self._function_list.update({reference.__name__: reference})

    def _stop(self):
        self._global_stop_event.set()
        self._close()

    def _close(self):
        self._s.shutdown(socket.SHUT_RDWR)
        self._s.close()


class Connection(Thread):
    def __init__(self, s, address, exec_controller, global_stop_event, lock):
        super(Connection, self).__init__()
        self._s = s
        self._address = address
        self._exec_controller = exec_controller
        self._lock = lock
        self._global_stop_event = global_stop_event
        self._local_stop_event = Event()
        self.daemon = True

    def run(self):
        while not self._global_stop_event.is_set() and not self._local_stop_event.is_set():
            try:
                raw_data = self._s.recv(ProtocolDataUnit.MAX_LENGTH)
            except socket.timeout as _:
                break
            if not raw_data:
                break
            pdu_in = ProtocolDataUnit()
            pdu_out = ProtocolDataUnit()
            try:
                pdu_in.loads(raw_data)
                with self._lock:  # TODO: Move it to excecution_controller.ExecutionController
                    returned_value = self._exec_controller.call(
                        pdu_in.func_name, pdu_in.func_args)
            except InternalServerError as _:
                pdu_out.set_exception(0)
            except FunctionNotDefinedError as _:
                pdu_out.set_exception(1)
            except WrongArgumentsError as _:
                pdu_out.set_exception(2)
            except PDUFieldNotExistsError as _:
                pdu_out.set_exception(3)
            except MessageTooLongError as _:
                pdu_out.set_exception(4)
            except BadPDUFormatError as _:
                pdu_out.set_exception(5)
            else:
                pdu_out.set_response(returned_value)
            self._s.sendall(pdu_out.dumps())
        self._close()

    def _close(self):
        self._local_stop_event.set()
        try:
            self._s.shutdown(socket.SHUT_RDWR)
        except OSError as _:
            pass
        self._s.close()
