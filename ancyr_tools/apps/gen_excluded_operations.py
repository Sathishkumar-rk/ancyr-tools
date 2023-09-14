import argparse
import logging
from ancyr_tools.symbol_parser import parse_symbol_file
from pathlib import Path


def cmdline():
    parser = argparse.ArgumentParser(
        description="Using the provided symbol file and included operations lists/files, generate an excluded operation list."
                    "Output is a comma-separated list, suitable as an argument to gcc/g++."
    )
    parser.add_argument('symbol_file', type=Path)
    parser.add_argument('-l', '--included_operation_list', type=str, nargs="*", default=[],
                      help="A list of functions that should be ignored when generating the excluded operations list")
    parser.add_argument('-f', '--included_operation_file', type=str, nargs="*", default=[],
                      help="Files containing functions that should be ignored when generating the excluded operations list")
    parser.add_argument('-e', '--excluded_operation_list', type=str, nargs="*", default=[],
                        help="A list of excluded operations -- this can reduce the size of your excluded operation list")
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    included_operations = args.included_operation_list

    excluded_operations = []
    output = ''

    for f in args.included_operation_file:
        with open(f) as fpt:
            included_operations += fpt.readlines()

    _, function_names = parse_symbol_file(args.symbol_file)

    logging.debug(f"FUNCTION NAMES: {function_names}")
    logging.debug(f"INCLUDED FUNCTIONS: {included_operations}")

    for fun in function_names:
        excluded = True
        function_string = fun.split("(")[0]
        function_string = function_string.split("<")[0]
        function_string = function_string.split(" ")[-1]
        for op in included_operations:
            if function_string.startswith(op):
                excluded = False
                break
        if excluded:
            # Don't add this operation to the excluded operation list if it would already be excluded
            excluded = True
            for op in args.excluded_operation_list:
                if op in function_string:
                    excluded = False
                    break
        if excluded:
            excluded_operations.append(function_string)
            output += f"'{function_string}',"



    # Add our excluded operations list passed by the user
    for op in args.excluded_operation_list:
        excluded_operations.append(op)
        output += f"'{op}',"

    print(output.rstrip(","))

if __name__ == '__main__':
    cmdline()