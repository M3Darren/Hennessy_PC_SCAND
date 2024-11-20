from get_log import m_logger


class CustomBaseException(Exception):
    """ 所有自定义异常的基类 """

    def __init__(self, message, *args):
        super().__init__(message, *args)
        self.message = message

    def __str__(self):
        return f"\033[31m[CustomBaseException] {self.message}\033[0m"


class ApplicationException(CustomBaseException):
    """ 通用应用程序异常 """

    def __init__(self, message="An error occurred in the application", *args):
        m_logger.error(message)
        super().__init__(message, *args)


class FileNotFoundException(CustomBaseException):
    """ 文件未找到异常 """

    def __init__(self, filename, message="File not found", *args):
        m_logger.error(f"{message}: '{filename}'")
        super().__init__(f"{message}: '{filename}'", *args)
        self.filename = filename


class FileReadException(CustomBaseException):
    """ 文件未找到异常 """

    def __init__(self, filename, message="File read error", *args):
        m_logger.error(f"{message}: {filename}")
        super().__init__(f"{message}: {filename}", *args)
        self.filename = filename


class FilePermissionException(CustomBaseException):
    """ 文件权限异常 """

    def __init__(self, filename, message="Permission error with file", *args):
        m_logger.error(f"{message}: {filename}")
        super().__init__(f"{message}: {filename}", *args)
        self.filename = filename
