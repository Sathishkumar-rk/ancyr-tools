import argparse
import re
import glob
import os
import pandas as pd
import cxxfilt


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


def parseArguments():
    args = argparse.ArgumentParser()
    args.add_argument('--symbol_file', type=str, required=True)
    args.add_argument('--input_dir', type=str, required=False)
    args.add_argument('--output_dir', type=str, required=True)
    args.add_argument('--path_operations', type=str, required=False)
    args.add_argument('--excluded_operations', type=str, required=True)
    args.add_argument('--csv_file', type=str, required=False)
    args_dict = vars(args.parse_args())

    if args_dict['input_dir'] is None:
        args_dict['input_dir'] = os.path.dirname(args_dict['symbol_file'])

    if args_dict['output_dir'] is None:
        args_dict['output_dir'] = args_dict['input_dir']

    if args_dict['path_operations'] is not None:
        ids_path = ids_path_file_parser(args_dict['path_operations'])
        ops = set([op for path in ids_path for op in path])
        args_dict['path_operations'] = ops
    else:
        args_dict['path_operations'] = []


    if args_dict['excluded_operations'] is not None:
        excluded_operations = []
        with open(args_dict['excluded_operations'], 'r') as f:
            for l in f:
                excluded_operations.append(l.strip())
        del args_dict['excluded_operations']
        args_dict['excluded_operations'] = excluded_operations

    return args_dict


def parseSymbolFile(args):
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
                name = name.split(".hidden ")[-1] # Required for c++ functions
                try:
                    name = cxxfilt.demangle(name)
                except cxxfilt.InvalidName:
                    pass
                # Get rid of any class names
                name = name.split("::")[-1]
                # Get rid of function paramenters
                name = name.split("(")[0]
                name = name.split("<")[0]
                name = name.split(">")[0]
                name = name.split("&")[0]
                name = name.split(")")[0]
                name = name.split(",")[0]
                name = name.split(" ")[0]
                if name in args['excluded_operations']:
                    continue
                if name not in func:
                    func.append(name)
                func.append(name)
                result['from_offset'][offset] = {'name': name}
                result['from_name'][name] = {'offset': offset}

    return result


def generateFuncitonIndices(syms, csv, args):
    if csv is not None:
        csv_names = csv['from_name'].keys();
    else:
        csv_names = []

    syms['from_index'] = {}

    sym_names = syms['from_name'].keys()

    used_indices = []
    for csv_name in csv_names:
        if csv_name in sym_names:
            csv_index = csv['from_name'][csv_name]['index']
            used_indices.append(csv_index)
            syms['from_name'][csv_name]['index'] = csv_index
            sym_offset = syms['from_name'][csv_name]['offset']
            syms['from_offset'][sym_offset]['index'] = csv_index
            syms['from_index'][csv_index] = {'name': csv_name, 'offset': sym_offset}

    index = 0
    for sym_name in syms['from_name'].keys():
        if sym_name not in args['path_operations']:
            continue

        while index in used_indices:
            index = index + 1

        used_indices.append(index)
        syms['from_name'][sym_name]['index'] = index
        offset = syms['from_name'][sym_name]['offset']
        syms['from_offset'][offset]['index'] = index
        syms['from_index'][index] = {'name': sym_name, 'offset': offset}

    sym_offsets = sorted(syms['from_offset'].keys())
    for sym_offset in sym_offsets:
        if syms['from_offset'][sym_offset].get('index') is not None:
            continue

        # while index in used_indices:
        #     index = index + 1
        index = 0xFFFF

        used_indices.append(index)
        syms['from_offset'][sym_offset]['index'] = index
        sym_name = syms['from_offset'][sym_offset]['name']
        syms['from_name'][sym_name]['index'] = index
        syms['from_index'][index] = {'name': sym_name, 'offset': sym_offset}


def annotateCsvFiles(args, syms):
    if args.get('input_dir') is None:
        return

    input_dir = args['input_dir']
    output_dir = args['output_dir']

    files = glob.glob(input_dir + '/ids_func_*.csv')
    regex = re.compile(r'.*(ids_func_)(0x[0-9a-f]*).csv', flags=re.DOTALL)
    for f in files:
        match = regex.match(f);
        if not match:
            continue
        prefix, offset = match.groups()
        int_offset = int(offset, 16)

        if syms['from_offset'].get(int_offset) is not None:
            function_name = syms['from_offset'][int_offset]['name']
            output_file = output_dir + "/" + prefix + function_name + '.csv'
        else:
            output_file = output_dir + "/" + prefix + offset + '_annotated.csv'

        with open(f, 'r') as input, open(output_file, 'a') as output:
            for line in input:
                offset, rest = line.split(',', maxsplit=1)
                int_offset = int(offset, 16)
                if syms['from_offset'].get(int_offset) is not None:
                    function_name = syms['from_offset'][int_offset]['name']
                else:
                    function_name = "_"
                    output.write(function_name + "," + offset + "," + rest)


def loadCSVFile(args):
    if args.get('csv_file') is None:
        return None

    csv = {'from_name': {}, 'from_index': {}}
    with open(args['csv_file'], 'r') as file:
        for line in file:
            name, offset, index = line.split(",")
            index = int(index, 0)
            offset = int(offset, 16)
            csv['from_name'][name] = {"offset": offset, "index": index}
            csv['from_index'][index] = {"name": name, "offset": offset}

    return csv


def generateIndexCSource(args, syms):
    offs = sorted(syms['from_offset'].keys())
    indices = sorted(syms['from_index'].keys())
    max_operation_id = max(indices) + 1
    print(f"MAX_OPERATIONID: {max_operation_id}")
    min_off = offs[0]
    max_off = offs[-1]

    count = max_off - min_off + 1

    output_dir = args['output_dir']
    c_file = output_dir + "/" + "operation_id_map.c"
    h_file = output_dir + "/" + "operation_id_map.h"
    csv_file = output_dir + "/" + "operation_id_map.csv"

    with open(h_file, 'w') as h_out:
        h_out.write("#ifndef __OFFSET_TO_OPERATIONID_H__\n")
        h_out.write("#define __OFFSET_TO_OPERATIONID_H__\n\n")
        h_out.write("#include <stdint.h>\n\n")
        h_out.write(f"#define OFFSET_TO_OPERATIONID_SIZE {count}\n")
        h_out.write(f"#define OPERATIONID_TO_OFFSET_SIZE {max_operation_id}\n")
        h_out.write(f"#define ADDRESS_OFFSET 0x{min_off:016x}\n\n")
        h_out.write("extern const uint16_t OFFSET_TO_OPERATIONID[OFFSET_TO_OPERATIONID_SIZE];\n")
        h_out.write("extern const uint32_t OPERATIONID_TO_OFFSET[OPERATIONID_TO_OFFSET_SIZE];\n\n")
        h_out.write("static inline uint16_t offset_to_operationid(uint64_t offset)\n")
        h_out.write("{\n")
        h_out.write("    return OFFSET_TO_OPERATIONID[offset - ADDRESS_OFFSET];\n")
        h_out.write("}\n\n")
        h_out.write("static inline uint32_t operationid_to_offset(uint16_t index)\n")
        h_out.write("{\n")
        h_out.write("    return OPERATIONID_TO_OFFSET[index];\n")
        h_out.write("}\n\n")
        h_out.write("#endif\n")

    # TODO:
    # csv file can be used to ensure the same mapping as things move around.
    # this may or may not be needed.
    with open(c_file, 'w') as c_out, open(csv_file, 'w') as csv_out:
        c_out.write("#include <stdint.h>\n")
        c_out.write("#include \"operation_id_map.h\"\n\n")
        c_out.write("const uint16_t OFFSET_TO_OPERATIONID[OFFSET_TO_OPERATIONID_SIZE] = {\n")
        for off in offs:
            name = syms['from_offset'][off]['name']
            index = syms['from_offset'][off]['index']
            key = off - min_off
            csv_out.write(f"{name},0x{off:x},{index}\n")
            c_out.write(f"    //{name},0x{off:x},{index}\n")
            c_out.write(f"    [0x{key:08x}] = {index},\n")
        c_out.write("};\n\n")

        c_out.write("const uint32_t OPERATIONID_TO_OFFSET[OPERATIONID_TO_OFFSET_SIZE] = {\n")
        for i in range(0, max_operation_id):
            if i in indices:
                name = syms['from_index'][i]['name']
                off = syms['from_index'][i]['offset']
                c_out.write(f"    //{name},0x{off:x},{i}\n")
                c_out.write(f"    [{i}] = 0x{off:08x},\n")
            else:
                c_out.write(f"    //_,0x0,{i}\n")
                c_out.write(f"    [{i}] = 0x0,\n")
        c_out.write("};\n\n")

    cmd = "cp {0} {1}".format(c_file, args['output_dir'])
    os.system(cmd)
    cmd = "cp {0} {1}".format(h_file, args['output_dir'])
    os.system(cmd)


def cmdline():
    args = parseArguments()
    syms = parseSymbolFile(args)
    csv = loadCSVFile(args)
    generateFuncitonIndices(syms, csv, args)
    generateIndexCSource(args, syms)
    annotateCsvFiles(args, syms)

if __name__ == '__main__':
    cmdline()

