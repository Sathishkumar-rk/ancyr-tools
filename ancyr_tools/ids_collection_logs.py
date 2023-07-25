from pathlib import Path
import csv


class IdsCollectionSample:

    def __init__(self, offset: int, cycles: int, icache_misses: int, dcache_misses: int, seconds: float):
        self.offset = offset
        self.cycles = cycles
        self.icache_misses = icache_misses
        self.dcache_misses = dcache_misses
        self.seconds = seconds

    @staticmethod
    def load_ids_collection_log(sample_file: Path) -> ["IdsCollectionSample"]:
        retval = []
        with open(sample_file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                # print(f"row: {row}")
                retval.append(
                    IdsCollectionSample(
                        int(row[0], 0), int(row[1]), int(row[2]), int(row[3]), float(row[4])
                    )
                )
        return retval

    @staticmethod
    def get_function_names(ids_samples: ["IdsCollectionSample"], symbols_by_offset: dict) -> [str]:
        """
        Get a list of the function names for the provided ids_samples array and the samples dictionary
        :param ids_samples:
        :param symbols_by_offset:
        :return:
        """
        retval = []
        for sample in ids_samples:
            if sample.offset not in symbols_by_offset:
                retval.append(hex(sample.offset))
            else:
                retval.append(symbols_by_offset[sample.offset]["name"])
        return retval

