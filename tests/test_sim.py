import pysv.util
from pysv import sv, compile_lib, DataType, generate_cxx_binding
import tempfile
import pytest
import os


class BoxFilter:
    @sv()
    def __init__(self, filter_size):
        self.__values = [0 for _ in range(filter_size)]
        self.__ptr = 0

    @sv(value=DataType.UInt, return_type=DataType.Void)
    def push(self, value):
        self.__values[self.__ptr] = value
        self.__ptr = (self.__ptr + 1) % len(self.__values)

    @sv(return_type=DataType.UInt)
    def avg(self):
        result = 0
        for v in self.__values:
            result += v
        return result // len(self.__values)


@pytest.mark.skipif(not pysv.util.is_verilator_available(), reason="Verilator not available")
def test_verilator(get_vector_filename):
    with tempfile.TemporaryDirectory() as temp:
        lib_path = compile_lib([BoxFilter], cwd=temp)
        header_file = os.path.join(os.path.abspath(temp), "box_filter.hh")
        generate_cxx_binding([BoxFilter], filename=header_file)

        # we have three files
        # the sv file, the driver file, and the header
        sv_file = get_vector_filename("test_verilator_boxfilter.sv")
        driver = get_vector_filename("test_verilator_boxfilter.cc")
        # just run teh verilator
        tester = pysv.util.VerilatorTester(lib_path, sv_file, header_file, driver, cwd=temp)
        tester.run()


if __name__ == "__main__":
    from conftest import get_vector_filename_fn
    test_verilator(get_vector_filename_fn)

