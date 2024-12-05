import os
import sys
import time

from comparison_operation import ComparisonOperation
from file_exception import CustomBaseException
from get_log import m_logger
from load_operation import LoadOperation

# 如果程序打包为可执行文件
if getattr(sys, 'frozen', False):
    # 获取可执行文件所在的目录
    BASE_PATH = os.path.dirname(sys.executable)
    print(f'EXE执行路径：{BASE_PATH}')
    # 将当前工作目录设置为可执行文件所在的目录
    os.chdir(BASE_PATH)
else:
    # 如果程序作为脚本运行，使用脚本目录
    BASE_PATH = os.path.dirname(__file__)
    print(f'脚本执行路径：{BASE_PATH}')
    os.chdir(BASE_PATH)


class Application:
    __load_operation = None
    __comparison_operation = None
    __merge_objs = None
    __case_objs = None
    __result_list = []
    __print_filename = ''
    __print_result = ''

    def __init__(self):
        print("compare loading...")
        LoadOperation.check_resources_exist()
        self.__load_operation = LoadOperation()
        self.__comparison_operation = ComparisonOperation()
        self.__merge_objs = self.__load_operation._merge_queue
        self.__case_objs = self.__load_operation._case_queue

    def main(self):
        start_time = time.time()
        m_logger.info("============ Compare Begin ===============")
        while not self.__case_objs.empty():
            case = self.__case_objs.get()
            file_obj = self.__merge_objs.get()
            result = self.deconstructing_obj(file_obj, case)
            case['result'] = self.result_converted(result)
            self.__result_list.append(case['result'])
            print(f"{self.__print_filename:<60}{self.__print_result:<10}")
            self.__print_filename = ''
            m_logger.info(f"result：{case['result']}")
        self.__load_operation.write_to_caseFile_result(self.__result_list, self.__comparison_operation._remarks_list)
        m_logger.info("============ Compare End ===============")
        end_time = time.time()
        print(f"Compared time: {end_time - start_time:.2f} seconds")
        m_logger.info(f"Compared time: {end_time - start_time:.2f} seconds")
        self.__load_operation.backup_file()

    def deconstructing_obj(self, merge_objs, case_obj):
        if isinstance(merge_objs, tuple):
            m_logger.info("@@@@@@@@@@@@@@@@@ [ duplex scanning ] @@@@@@@@@@@@@@@@@")
            double_sided_flag = True
            file_name = '('
            for index, obj in enumerate(merge_objs):
                file_name += obj['filename'] + '&'
                double_sided_flag = self.__comparison_operation.compare_main({**obj, **case_obj}, page_index=index)
                if not double_sided_flag:
                    double_sided_flag = False
                    break
            self.__print_filename = file_name + ')'
            return double_sided_flag
        else:
            self.__print_filename = merge_objs['filename']
            return self.__comparison_operation.compare_main({**merge_objs, **case_obj})

    def result_converted(self, r_bool):
        if r_bool:
            self.__print_result = "\033[32mPass\033[0m"
            return "Pass"
        else:
            self.__print_result = "\033[31mFail\033[0m"
            return "Fail"


try:
    start_time = time.time()
    Application().main()
    end_time = time.time()
    print(f"Total time: {end_time - start_time:.2f} seconds")
except CustomBaseException as e:
    print(e)
