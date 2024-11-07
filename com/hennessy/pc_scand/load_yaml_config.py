import os
import sys

import yaml

from com.hennessy.pc_scand.file_exception import FileNotFoundException, FileReadException


class LoadConfig:
    __yaml_file_path = "config/config.yml"
    if not os.path.exists(__yaml_file_path):
        raise FileNotFoundException(f"{__yaml_file_path}")
    # 读取YAML文件
    try:
        with open(__yaml_file_path, 'r', encoding='utf-8') as file:
            __yaml_data = yaml.load(file, Loader=yaml.FullLoader)
    except Exception as e:
        raise FileReadException(__yaml_file_path) from e

    @classmethod
    def load_yaml_papersize(cls):
        """
        加载配置文件,返回纸张尺寸
        """
        return cls.__yaml_data['papersize']

    @classmethod
    def load_yaml_error_range(cls):
        """
        加载配置文件,返回误差范围
        """
        return cls.__yaml_data['error_range']

    @classmethod
    def load_yaml_resources_path(cls, path):
        """
        加载配置文件,返回路径
        """
        return cls.__yaml_data['path']['prefix'] + cls.__yaml_data['path'][path]

    @classmethod
    def load_yaml_case_titles(cls, title):
        return cls.__yaml_data['options'].get(title)


_case_scaling_ratio = LoadConfig.load_yaml_case_titles("scaling_ratio")
_case_scanning_mode = LoadConfig.load_yaml_case_titles("scanning_mode")
_case_preservation_method = LoadConfig.load_yaml_case_titles("preservation_method")
_case_expected_bit_depth = LoadConfig.load_yaml_case_titles("expected_bit_depth")
_case_paper_size = LoadConfig.load_yaml_case_titles("paper_size")
_case_expected_dpi = LoadConfig.load_yaml_case_titles("expected_dpi")
