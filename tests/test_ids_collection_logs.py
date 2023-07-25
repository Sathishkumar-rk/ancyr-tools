from unittest import TestCase
from pathlib import Path
from ancyr_tools.ids_collection_logs import IdsCollectionSample
from ancyr_tools.symbol_parser import parse_symbol_file

SAMPLE_LOG_FILES_DIR = Path(__file__).parent.joinpath("samples", "ids_collection_logs")
SAMPLE_SYMBOL_FILES_DIR = Path(__file__).parent.joinpath("samples", "symbol_files")

# CSV file is formatted as:
# offset, hw cycles, i_cache misses, d_cache mises, real time

class TestLoadCollectionLogsFile(TestCase):
    def test_load_sample_collection_logs(self):
        sample_file = SAMPLE_LOG_FILES_DIR.joinpath("ids_func_0x10f70.csv")
        ids_samples = IdsCollectionSample.load_ids_collection_log(sample_file)
        self.assertEqual(5000, len(ids_samples))
        # Verify that the first sample is valid
        sample = ids_samples[0]
        self.assertEqual(74864, sample.offset)
        self.assertEqual(24371, sample.cycles)
        self.assertEqual(314, sample.icache_misses)
        self.assertEqual(140, sample.dcache_misses)
        self.assertEqual(18688.337555851, sample.seconds)

    def test_get_sample_function_names(self):
        sample_ids_log_file = SAMPLE_LOG_FILES_DIR.joinpath("ids_func_0x10f70.csv")
        sample_symbol_file = SAMPLE_SYMBOL_FILES_DIR.joinpath("sym.txt")
        symbols_by_offset, _ = parse_symbol_file(sample_symbol_file)

        ids_samples = IdsCollectionSample.load_ids_collection_log(sample_ids_log_file)
        function_names = IdsCollectionSample.get_function_names(ids_samples, symbols_by_offset)
        self.assertEqual(5000, len(function_names))