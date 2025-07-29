import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

current_path = os.path.dirname(__file__)

from simplejrpc_gfile import *


class TestFilerOperator(unittest.TestCase):
    """ """

    @unittest.skip
    def test_read_simple_file_operator(self):
        """ """
        test_file_name = "zack.log"
        filepath = os.path.join(current_path, test_file_name)
        sfo = SimpleFileOperator(filepath, auto_create=True)
        content = sfo.read()
        print("[*] content > ", content)

    @unittest.skip
    def test_write_simple_file_operator(self):
        """ """
        test_file_name = "zack.log"
        content = "1111"
        filepath = os.path.join(current_path, test_file_name)
        sfo = SimpleFileOperator(filepath, auto_create=True)
        content = sfo.write(content=content)
        print("[*] content > ", content)

    # @unittest.skip
    def test_write_json_file_operator(self):
        """ """
        test_file_name = "zack.json"
        filepath = os.path.join(current_path, test_file_name)
        jfo = JsonFileOperator(filepath, auto_create=True)
        content = {"name": "zack", "age": 111}
        content = jfo.write(content)
        print("[*] content > ", content)

    @unittest.skip
    def test_read_json_file_operator(self):
        """ """
        test_file_name = "zack.json"
        filepath = os.path.join(current_path, test_file_name)
        jfo = JsonFileOperator(filepath, auto_create=True)
        content = jfo.read()
        print("[*] content > ", content)

    # @unittest.skip
    def test_read_big_file_operator(self):
        """ """
        test_file_name = "zack.log"
        filepath = os.path.join(current_path, test_file_name)
        jfo = BigFileOperator(filepath, auto_create=True)
        content = jfo.read(num=10, p=1)
        print("[*] content > ", content)


if __name__ == "__main__":
    """ """
    unittest.main()
