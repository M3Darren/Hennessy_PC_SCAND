import datetime
import logging
import os


class GetLog:
    __logger = None
    current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
    log_file_name = f"implementation.log"
    log_path = f'log/{current_time}'
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    __file_path = f"{log_path}/{log_file_name}"

    @classmethod
    def get_logger(cls):
        if cls.__logger is None:
            # 定义自定义日志级别和数值
            NOTICE_LEVEL = 25
            logging.addLevelName(NOTICE_LEVEL, "NOTICE")

            # 扩展 Logger 类，添加自定义日志级别的方法
            def notice(self, message, *args, **kwargs):
                if self.isEnabledFor(NOTICE_LEVEL):
                    self._log(NOTICE_LEVEL, message, args, **kwargs)

            logging.Logger.notice = notice  # 给 Logger 添加方法
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
