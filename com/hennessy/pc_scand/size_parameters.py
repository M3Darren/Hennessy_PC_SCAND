from enum import Enum


class PaperSize(Enum):
    A5 = (5.83, 8.27)
    A4 = (8.27, 11.69)
    B5_ISO = (7.17, 10.12)

    @staticmethod
    def get_size(size_str):
        size = {
            'A5': PaperSize.A5.value,
            'A4': PaperSize.A4.value,
            'B5_ISO': PaperSize.B5_ISO.value,
        }
        return size.get(size_str, "Not Available")
