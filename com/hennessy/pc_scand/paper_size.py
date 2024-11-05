
from com.hennessy.pc_scand.load_yaml_config import LoadConfig


class PaperSize:
    sizes = LoadConfig().load_yaml_papersize()

    @classmethod
    def get_size(cls, name):
        size = cls.sizes.get(name)
        if size is None:
            print(f"Paper size '{name}' is not defined.")
            return "Unknown size"  # 或者返回其他合适地默认值
        return size
