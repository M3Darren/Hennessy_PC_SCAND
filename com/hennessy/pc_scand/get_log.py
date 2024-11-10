import datetime
import logging


class GetLog:
    __logger = None
    current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
    log_file_name = f"log_{current_time}.log"
    __file_path = f"log/{log_file_name}"

    @classmethod
    def get_logger(cls):
        if cls.__logger is None:
            cls.__logger = logging.getLogger()
            # 设置级别
            cls.__logger.setLevel(logging.INFO)
            # 4、设置日志的输出格式
            fmt = "[%(asctime)s] - %(levelname)s - [%(lineno)d)] : %(message)s"
            formatter = logging.Formatter(fmt)
            # 5、将日志输出格式添加到handler
            file_handler = logging.FileHandler(filename=cls.__file_path, encoding="utf-8")
            file_handler.setFormatter(formatter)
            # 6、将handler添加到logger
            cls.__logger.addHandler(file_handler)
        return cls.__logger


m_logger = GetLog.get_logger()
