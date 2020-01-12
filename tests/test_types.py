import json
import unittest

from pyrpc.common import exceptions
from pyrpc.common.types import ProtocolDataUnit

# TODO: Refactor it to proper testing form - separate TestCase for each function.


class TestProtocolDataUnit(unittest.TestCase):
    def setUp(self):
        self.pdu1_arguments = [
            b'{"func_name": "just_function", "func_args": ["text", 2]}']
        self.pdu2_arguments = []

        self.pdu1 = ProtocolDataUnit(*self.pdu1_arguments)
        self.pdu2 = ProtocolDataUnit(*self.pdu2_arguments)

    def test_set(self):
        payload1 = {"returned": "secret_message"}
        payload2 = {"error": 1}

        self.pdu1.set(payload1)
        self.pdu2.set(payload2)

        self.assertEqual(self.pdu1.__dict__, payload1)
        self.assertEqual(self.pdu2.__dict__, payload2)

    def test_set_bad_value(self):
        wrong_payload1 = ["hello", "world"]
        wrong_payload2 = "there_is_no_value_here"

        with self.assertRaises(exceptions.BadPDUFormatError):
            self.pdu1.set(wrong_payload1)
            self.pdu2.set(wrong_payload2)

    def test_get(self):
        pdu1_verification = json.loads(
            self.pdu1_arguments[0]) if self.pdu1_arguments else {}
        pdu2_verification = json.loads(
            self.pdu2_arguments[0]) if self.pdu2_arguments else {}

        pdu1_result = self.pdu1.get()
        pdu2_result = self.pdu2.get()

        self.assertEqual(pdu1_result, pdu1_verification)
        self.assertEqual(pdu2_result, pdu2_verification)

    def test_loads(self):
        raw_data_verification1 = {"returned": "secret_message"}
        raw_data_verification2 = {"error": 1}

        raw_data1 = b'{"returned": "secret_message"}'
        raw_data2 = b'{"error": 1}'

        self.pdu1.loads(raw_data1)
        self.pdu2.loads(raw_data2)

        self.assertEqual(self.pdu1.__dict__, raw_data_verification1)
        self.assertEqual(self.pdu2.__dict__, raw_data_verification2)

    def test_loads_bad_value(self):
        wrong_raw_data1 = "Hello, world!"
        wrong_raw_data2 = 1

        with self.assertRaises(exceptions.BadPDUFormatError):
            self.pdu1.loads(wrong_raw_data1)
            self.pdu2.loads(wrong_raw_data2)

    def test_loads_max_lenght(self):
        raw_data1 = bytes('{"a": "%s"}' % (
            "A" * (ProtocolDataUnit.MAX_LENGTH - 11)), 'utf-8')
        wrong_raw_data2 = bytes('{"b": "%s"}' % (
            "B" * ProtocolDataUnit.MAX_LENGTH * 2), 'utf-8')

        self.pdu1.loads(raw_data1)

        with self.assertRaises(exceptions.MessageTooLongError):
            self.pdu2.loads(wrong_raw_data2)

    def test_dumps(self):
        raw_data_verification1 = self.pdu1_arguments[0] if self.pdu1_arguments else b"{}"
        raw_data_verification2 = self.pdu2_arguments[0] if self.pdu2_arguments else b"{}"

        raw_data_result1 = self.pdu1.dumps()
        raw_data_result2 = self.pdu2.dumps()

        self.assertEqual(raw_data_result1, raw_data_verification1)
        self.assertEqual(raw_data_result2, raw_data_verification2)

    def test_set_request(self):
        function_name1 = "function_add"
        function_name2 = "functionSubstract"

        function_args1 = ["Hello", "World", 1]
        function_args2 = [{}, []]

        pdu1_verification = {"func_name": function_name1,
                             "func_args": function_args1}
        pdu2_verification = {"func_name": function_name2,
                             "func_args": function_args2}

        self.pdu1.set_request(function_name1, function_args1)
        self.pdu2.set_request(function_name2, function_args2)

        self.assertEqual(self.pdu1.__dict__, pdu1_verification)
        self.assertEqual(self.pdu2.__dict__, pdu2_verification)

    def test_set_request_bad_value(self):
        wrong_function_name1 = b'Hello, world!'
        wrong_function_name2 = 1

        wrong_function_args1 = "Hello, world!"
        wrong_function_args2 = 1

        with self.assertRaises(exceptions.BadPDUFormatError):
            self.pdu1.set_request(wrong_function_name1, wrong_function_args1)
            self.pdu2.set_request(wrong_function_name2, wrong_function_args2)

    def test_set_response(self):
        returned_value1 = 3.14
        returned_value2 = None

        pdu1_verification = {"func_returned": 3.14}
        pdu2_verification = {"func_returned": None}

        self.pdu1.set_response(returned_value1)
        self.pdu2.set_response(returned_value2)

        self.assertEqual(self.pdu1.__dict__, pdu1_verification)
        self.assertEqual(self.pdu2.__dict__, pdu2_verification)
