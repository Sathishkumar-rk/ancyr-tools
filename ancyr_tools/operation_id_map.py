from pathlib import Path
import csv


def write_operation_id_map(output_file: Path, map_data: {str: int}) -> None:
    """
    Write the operation ID map to the provided file.  Map data should be sorted by name.
    :param output_file:
    :param map_data:
    :return:
    """
    with open(output_file, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for name, value in map_data.items():
            offset = value['offset']
            if "index" in value:
                index = value['index']
            else:
                index = 0xFFFF
            csv_writer.writerow([name, hex(offset), index])
