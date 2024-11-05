from enum import Enum

from com.hennessy.pc_scand.global_file import CONFIG_DATA


class PaperSize(Enum):
    A4 = (8.27, 11.69)
    A5 = (5.83, 8.27)
    B5_JIS = (7.17, 10.12)
    B5_ISO = (6.93, 9.84)

    @staticmethod
    def get_size(size_str):
        size = {
            'A5': PaperSize.A5.value,
            'A4': PaperSize.A4.value,
            'B5_ISO': PaperSize.B5_ISO.value,
            'B5_JIS': PaperSize.B5_JIS.value
        }
        return size.get(size_str, "Not Available")
