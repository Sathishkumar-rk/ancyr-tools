from pathlib import Path
import csv


class IdsCollectionSample:

    def __init__(self, offset: str, cycles: int, icache_misses: int, dcache_misses: int, seconds: float):
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
                        row[0], int(row[1]), int(row[2]), int(row[3]), float(row[4])
                    )
                )
        return retval
