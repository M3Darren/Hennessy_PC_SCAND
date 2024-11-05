import yaml


class LoadConfig:
    __yaml_file_path = "./config/config.yml"

    # 读取YAML文件
    with open(__yaml_file_path, 'r', encoding='utf-8') as file:
        __yaml_data = yaml.load(file, Loader=yaml.FullLoader)

    @classmethod
    def load_yaml_papersize(cls):
        """
        加载配置文件,返回纸张尺寸
        """
        return cls.__yaml_data['papersize']

    @classmethod
    def load_yaml_path(cls, path):
        """
        加载配置文件,返回路径
        """
        return cls.__yaml_data['path']['prefix'] + cls.__yaml_data['path'][path]

    @classmethod
    def load_yaml_error_range(cls):
        """
        加载配置文件,返回误差范围
        """
        return cls.__yaml_data['error_range']


