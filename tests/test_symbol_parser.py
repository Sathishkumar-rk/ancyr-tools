from unittest import TestCase
import pathlib
from ancyr_tools.symbol_parser import parse_symbol_file, load_operation_id_map_file

SAMPLE_SYMBOL_FILES_DIR = pathlib.Path(__file__).parent.joinpath("samples", "symbol_files")
SAMPLE_OPERATION_ID_MAP_FILES_DIR = pathlib.Path(__file__).parent.joinpath("samples", "operation_id_maps")

class TestSymbolParser(TestCase):
    def test_sample_symbol_files(self):
        sample_file = SAMPLE_SYMBOL_FILES_DIR.joinpath("sym.txt")
        symbols_by_offset, symbols_by_name = parse_symbol_file(sample_file)
        # Make sure the length of the two results are the same
        self.assertEqual(len(symbols_by_offset), len(symbols_by_name))
        # Make sure the symbols and names match
        for offset, value in symbols_by_offset.items():
            name = value["name"]
            self.assertIn(name, symbols_by_name)
            self.assertEqual(symbols_by_name[name]["offset"], offset)

    def test_sample_operation_id_maps(self):
        sample_file = SAMPLE_OPERATION_ID_MAP_FILES_DIR.joinpath("adas-demo-map.csv")
        symbols_by_offset, symbols_by_name = load_operation_id_map_file(sample_file)
        self.assertEqual(len(symbols_by_offset), len(symbols_by_name))
        # Make sure the length of the two results are the same
        self.assertEqual(len(symbols_by_offset), len(symbols_by_name))
        # Make sure the symbols and names match
        for offset, value in symbols_by_offset.items():
            name = value["name"]
            self.assertIn(name, symbols_by_name)
            self.assertEqual(symbols_by_name[name]["offset"], offset)