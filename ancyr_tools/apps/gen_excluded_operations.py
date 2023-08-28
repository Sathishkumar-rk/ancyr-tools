import argparse
import re
import pandas as pd
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
    args = parser.parse_args()

    included_operations = args.included_operation_list

    excluded_operations = []
    output = ''

    for f in args.included_operation_file:
        with open(f) as fpt:
            included_operations += fpt.readlines()

    _, function_names = parse_symbol_file(args.symbol_file)

    for n in function_names:
        if n not in included_operations:
            excluded_operations.append(n)
            output += f"'{n}',"

    print(output)

if __name__ == '__main__':
    cmdline()