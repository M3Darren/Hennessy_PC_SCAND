import os
import sys
from pathlib import Path

import yaml

YAML_FILE_PATH = './config/config.yml'


def get_executable_path():
    """Get the path of the executable file."""
    if getattr(sys, 'frozen', False):  # if running in a bundle
        return Path(sys.executable).parent
    else:  # if running in a script
        return Path(__file__).parent


def get_resource_folder_path(res):
    """Get the path of the 'image' folder."""
    executable_path = get_executable_path() / CONFIG_DATA.get('path')[res]
    # 判断文件是否存在
    if not os.path.exists(executable_path):
        raise FileNotFoundError(f"The file {executable_path} does not exist.")
    return


def read_yaml_file(file_path):
    """
    读取YAML文件并返回其内容作为Python字典。

    :param file_path: YAML文件的路径
    :return: 包含YAML文件内容的字典
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as exc:
            print(f"Error in configuration file: {exc}")
            return None


CONFIG_DATA = read_yaml_file(YAML_FILE_PATH)
if __name__ == "__main__":

    if CONFIG_DATA:
        print(CONFIG_DATA.get('paper_size')['A4'][0])
