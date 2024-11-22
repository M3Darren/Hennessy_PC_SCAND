from file_exception import ApplicationException
from load_yaml_config import LoadConfig


class PaperSize:
    sizes = LoadConfig().load_yaml_papersize()

    @classmethod
    def get_size(cls, name):
        size = cls.sizes.get(name)
        if size is None:
            raise ApplicationException(
                f'The "{name}" paper size appears in the case file. Please check whether it is configured in the "config/config.yml" file papersize attribute')
        return size
