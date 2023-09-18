from pathlib import Path
import argparse
from ancyr_tools.symbol_parser import parse_symbol_file
from ancyr_tools.ids_collection_logs import IdsCollectionSample
from ancyr_tools.operation_id_map import write_operation_id_map
import logging


def cmdline():
    parser = argparse.ArgumentParser(
        description="Using the provided symbol file and included operations lists/files, generate an operation ID map file"
                    "Output is a comma-separated list, suitable as an argument to gcc/g++."
    )
    parser.add_argument('symbol_file', type=Path)
    parser.add_argument('output_file', type=Path)
    parser.add_argument('-l', '--included_operation_list', type=str, nargs="*", default=[],
                      help="A list of functions that should be ignored when generating the excluded operations list")
    parser.add_argument('-f', '--included_operation_file', type=str, nargs="*", default=[],
                      help="Files containing functions that should be ignored when generating the excluded operations list")
    parser.add_argument('-e', '--excluded_operation_list', type=str, nargs="*", default=[],
                        help="A list of excluded operations -- this can reduce the size of the arguments passed to c++ (try using with '__')")
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    symbols_by_offset, symbols_by_name = parse_symbol_file(args.symbol_file)
    ids_samples = IdsCollectionSample.load_ids_collection_log(args.log_file)
    function_names = IdsCollectionSample.get_function_names(ids_samples, symbols_by_offset)
    unique_symbols = {}
    for f in function_names:
        if f not in unique_symbols:
            unique_symbols[f] = symbols_by_name[f]
    write_operation_id_map(args.output_file, unique_symbols)

if __name__ == "__main__":
    cmdline()