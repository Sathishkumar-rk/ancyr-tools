from pathlib import Path
import re
import cxxfilt
import csv
import logging
from typing import Iterable


def parse_symbol_file(symbol_file: Path) -> ({int: str}, {str: int}):
    """
    Parse the symbol file and return two dictionaries; the first contains the symbols sorted by offset,
    the second is symbols sorted by name
    :param symbol_file:
    :return: example:
    (
        {
            0x1234: {name: main}
        },
        {
            main: {offset: 0x1234}
        }
    )
    """
    func = []
    result_by_offset = {}
    result_by_name = {}
    with open(symbol_file, 'r') as f:
        regex = re.compile(r'^([0-9a-f]{16}).*([0-9a-f]{16})\s*(.*)$', flags=re.DOTALL)
        for l in f:
            match = regex.match(l)
            if match:
                groups = match.groups()
                offset = int(groups[0], 16)
                length = int(groups[1], 16)
                name = groups[2].strip()
                name = name.split(".hidden ")[-1]  # Required for c++ functions
                try:
                    name = cxxfilt.demangle(name)
                except cxxfilt.InvalidName:
                    logging.warning(f"Object Name {name} cannot be demangled")
                    pass
                if name not in func:
                    func.append(name)
                    result_by_offset[offset] = {'name': name}
                    result_by_name[name] = {'offset': offset}

    return result_by_offset, result_by_name


def sort_included_excluded_ops(
        function_names: {str, int},
        included_operations: Iterable[str],
        excluded_operations_input: Iterable[str]
) -> ([str], {str, int}):
    excluded_operations_output = []
    included_operations_output = {}
    for fun in function_names:
        excluded = True
        function_string = fun.split("(")[0]
        function_string = function_string.split("<")[0]
        function_string = function_string.split(" ")[-1]
        if not function_string:
            continue
        for op in included_operations:
            if function_string.startswith(op):
                excluded = False
                included_operations_output[function_string] = function_names[fun]['offset']
                break
        if excluded:
            # Don't add this operation to the excluded operation list if it would already be excluded
            excluded = True
            for op in excluded_operations_input:
                if op in function_string:
                    excluded = False
        if excluded:
            excluded_operations_output.append(function_string)
    return excluded_operations_output, included_operations_output

def load_operation_id_map_file(map_file: Path) -> ({int: str}, {str: int}):
    """
    Parse the symbol file and return two dictionaries; the first contains the symbols sorted by offset,
    the second is symbols sorted by name
    :param map_file:
    :return: example:
    (
        {
            0x1234: {name: main}
        },
        {
            main: {offset: 0x1234}
        }
    )
    """
    result_by_offset = {}
    result_by_name = {}
    with open(map_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            name = row[0]
            offset = int(row[1], 0)
            result_by_offset[offset] = {"name": name}
            result_by_name[name] = {"offset": offset}
    return result_by_offset, result_by_name
