from pathlib import Path
import re
import cxxfilt
import csv


def parse_symbol_file(symbol_file: Path) -> ({}, {}):
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
                    pass
                if name not in func:
                    func.append(name)
                    result_by_offset[offset] = {'name': name}
                    result_by_name[name] = {'offset': offset}

    return result_by_offset, result_by_name


def load_operation_id_map_file(map_file: Path) -> ({}, {}):
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
