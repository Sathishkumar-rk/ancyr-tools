import io
import csv


def generate_operation_id_map_string(map_data: {str: int}) -> None:
    """
    Generate the operation id map string.  Map data should be sorted by name.
    :param output_file:
    :param map_data:
    :return:
    """
    output = io.StringIO()
    csv_writer = csv.writer(output, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for name, value in map_data.items():
        offset = value['offset']
        if "index" in value:
            index = value['index']
        else:
            index = 0xFFFF
        csv_writer.writerow([name, hex(offset), index])
    return output.getvalue()
