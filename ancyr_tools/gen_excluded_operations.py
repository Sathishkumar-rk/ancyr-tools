import argparse
import re
import os
import pandas as pd
import cxxfilt


def parseArguments():
    args = argparse.ArgumentParser()
    args.add_argument('--input_dir', type=str, required=False)
    args.add_argument('--output_dir', type=str, required=False)
    args.add_argument('--symbol_file', type=str, required=True)
    args.add_argument('--path_operations', type=str, required=False)
    args.add_argument('--included_operations', type=str, required=True)
    args_dict = vars(args.parse_args())

    if args_dict['input_dir'] is None:
        args_dict['input_dir'] = os.path.dirname(args_dict['symbol_file'])

    if args_dict['output_dir'] is None:
        args_dict['output_dir'] = args_dict['input_dir']

    if args_dict['path_operations'] is not None:
        ids_path = ids_path_file_parser(args_dict['path_operations'])
        ops = set([op for path in ids_path for op in path])
        args_dict['path_operations'] = ops

    if args_dict['included_operations'] is not None:
        included_operations = []
        with open(args_dict['included_operations'], 'r') as f:
            for l in f:
                included_operations.append(l.strip())
        args_dict['included_operations'] = included_operations

    return args_dict


def exportExcludedOperations(args):
    regex = re.compile(r'^([0-9a-f]{16}).*([0-9a-f]{16})\s*(.*)$', flags=re.DOTALL)
    result = {"from_name": {}, 'from_offset': {}}
    func = []
    with open(args['symbol_file'], 'r') as f:
        for l in f:
            match = regex.match(l)
            if match:
                groups = match.groups()
                offset = int(groups[0], 16)
                length = int(groups[1], 16)
                name = groups[2].strip()
                name = name.strip(".hidden ") # Required for c++ functions
                try:
                    name = cxxfilt.demangle(name)
                except cxxfilt.InvalidName:
                    pass
                func.append(name)
                result['from_offset'][offset] = {'name': name}
                result['from_name'][name] = {'offset': offset}

    if args['path_operations'] is None:
        args['path_operations'] = []
    with open(args['output_dir'] + '/excluded_operations.ids', 'w') as file:
        for f in func:
            if f not in args['path_operations'] and f not in args['included_operations']:
                file.write(f)
                file.write('\n')


def ids_path_file_parser(file: str):
    paths = pd.read_csv(file, header=None)
    ids_path = []
    for path in paths.iloc:
        ops = []
        for op in path:
            if pd.isna(op) == False:
                ops.append(op)
        ids_path.append(ops)

    return ids_path


def cmdline():
    args = parseArguments()
    exportExcludedOperations(args)

if __name__ == '__main__':
    cmdline()