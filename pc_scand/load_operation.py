import io
import os
import shutil
from datetime import datetime, timedelta

import fitz
import queue
import openpyxl
import pandas as pd
from PIL import Image
import win32com.client as win32

from get_log import m_logger, GetLog
from file_exception import FileNotFoundException, ApplicationException
from load_yaml_config import LoadConfig, _case_scaling_ratio, _case_scanning_mode, \
    _case_preservation_method


class LoadOperation:
    """
    LoadOperation class
    """
    _case_queue = queue.Queue()  # case对象队列
    _merge_queue = queue.Queue()  # 合并对象队列
    __image_queue = queue.Queue()  # 图片对象队列
    __pdf_queue = queue.Queue()  # pdf对象队列
    __CASE_PATH = LoadConfig.load_yaml_resources_path("case_path")
    __IMAGE_PATH = LoadConfig.load_yaml_resources_path("image_path")
    __PDF_PATH = LoadConfig.load_yaml_resources_path("pdf_path")

    def __init__(self):
        """
        Constructor
        """
        m_logger.info('read case ...')
        self.load_case_and_convert()  # 读取用例并转化
        m_logger.info('read image .... ')
        self.load_image()  # 读取图片
        m_logger.info('read pdf ......')
        self.load_pdf()  # 读取pdf
        m_logger.info('merge data ........')
        self.constructive_load_data()  # 合并数据
        m_logger.info('data integrity check ........')
        # self.iterator(self._case_queue)

    @staticmethod
    def iterator(obj):
        """
        Traversal obj
        """
        for item in obj.queue:
            print(item)

    @classmethod
    def check_resources_exist(cls):
        """
        Check resources exist
        """
        cls.close_caseFile()
        cls.clear_overthrew_logs()
        if not os.path.exists(cls.__CASE_PATH):
            raise FileNotFoundException(cls.__CASE_PATH)
        if not os.path.exists(cls.__IMAGE_PATH):
            raise FileNotFoundException(cls.__IMAGE_PATH)
        if not os.path.exists(cls.__PDF_PATH):
            raise FileNotFoundException(cls.__PDF_PATH)

    def load_case_and_convert(self):
        """
        Load case and converter.
        """
        df = pd.read_excel(self.__CASE_PATH, sheet_name=0)
        for row in df.to_dict(orient='records'):
            scaling_str = row[_case_scaling_ratio]
            if not isinstance(scaling_str, str):
                scaling_str = scaling_str.strftime("%H:%M")
            row[_case_scaling_ratio] = int(scaling_str[-1])
            if row[_case_scanning_mode] == "输稿器（双面）":
                row[_case_scanning_mode] = 1
            if row[_case_preservation_method] == "PDF":
                row[_case_preservation_method] = 1
            self._case_queue.put(row)

    def load_image(self):
        """
        Load image
        将图片信息读入队列
        """
        image_dir = os.listdir(self.__IMAGE_PATH)
        if not image_dir:
            raise FileNotFoundException(self.__IMAGE_PATH, message='No image files found in the directory')
        for filename in sorted(image_dir):
            # 检查文件是否为图片格式（比如jpg或png）
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                # 获取图片的完整路径
                file_path = os.path.join(self.__IMAGE_PATH, filename)
                # 打开图片
                try:
                    img = Image.open(file_path)
                except Exception as e:
                    raise ApplicationException(f"{file_path} Read error")
                # 获取图片的宽度和高度
                width, height = img.size
                # 获取位深度
                depth = img.mode
                # 获取DPI
                dpi = img.info.get('dpi')
                # 保存图片信息
                image_info = {
                    'filename': filename,
                    'w_h': (width, height),
                    'actual_dpi': dpi,
                    'actual_bit_depth': depth,
                    'result': '',
                    'pil_image_obj': img
                }
                # 将信息添加到队列中
                self.__image_queue.put(image_info)

    def load_pdf(self):
        """
        Load pdf
        """
        pdf_dir = os.listdir(self.__PDF_PATH)
        if not pdf_dir:
            raise FileNotFoundException(self.__PDF_PATH, message='No files found in the directory')
        for filename in sorted(pdf_dir):
            # 检查文件格式
            if filename.lower().endswith('pdf'):
                # 获取PDF的完整路径
                pdf_path = os.path.join(self.__PDF_PATH, filename)
                # 打开PDF文件
                try:
                    doc = fitz.open(pdf_path)
                except Exception as e:
                    raise ApplicationException(f"{pdf_path} Read error")
                # 遍历PDF中的每一页
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    images = page.get_images(full=True)  # 获取页面中的所有图像
                    for img_index, img in enumerate(images):
                        xref = img[0]  # 图像的引用
                        base_image = doc.extract_image(xref)  # 提取图像为字节数据
                        image_bytes = base_image["image"]
                        # 使用Pillow打开图像
                        try:
                            pil_image = Image.open(io.BytesIO(image_bytes))
                        except Exception as e:
                            raise ApplicationException(
                                f"{pdf_path} Read error processing image on page {page_num + 1}, index {img_index + 1}")

                        depth = pil_image.mode
                        dpi = pil_image.info.get("dpi")  # 尝试获取DPI
                        # 获取图像的尺寸（宽度，高度）
                        width, height = pil_image.size
                        pdf_info = {
                            'filename': filename + '@page_' + str(page_num + 1),
                            'w_h': (width, height),
                            'actual_dpi': dpi,
                            'actual_bit_depth': depth,
                            'result': '',
                            'pil_image_obj': pil_image
                        }
                        self.__pdf_queue.put(pdf_info)

    def constructive_load_data(self):
        """
        Merge load data
        """

        def scanning_mode_judgment(queue_obj: queue.Queue):
            # 判断扫描方式为双面
            if case_item[_case_scanning_mode] == 1:
                if queue_obj.qsize() < 2:
                    raise ApplicationException(
                        f"{queue_obj.get()['filename']} The number of images is not enough")
                self._merge_queue.put((queue_obj.get(), queue_obj.get()))
            else:
                self._merge_queue.put(queue_obj.get())

        for case_item in self._case_queue.queue:
            if self.__image_queue.qsize() == 0 and self.__pdf_queue.qsize() == 0:
                raise ApplicationException(
                    f"Case exceed resources, Please check '{self.__CASE_PATH}'")
            # 判断保存方式为PDF
            if case_item[_case_preservation_method] == 1:
                scanning_mode_judgment(self.__pdf_queue)
            else:
                scanning_mode_judgment(self.__image_queue)
        if self.__image_queue.qsize() > 0 or self.__pdf_queue.qsize() > 0:
            raise ApplicationException(
                f"Resources exceed case, Please check '{self.__IMAGE_PATH}/' or '{self.__PDF_PATH}/'")

    def write_to_caseFile_result(self, result_list):
        sheet_name = 'Case'
        start_row = 2  # 假设从第2行开始追加（第1行通常是标题行）
        start_col = 1
        # 打开已存在的Excel文件
        workbook = openpyxl.load_workbook(self.__CASE_PATH)
        # 选择工作表
        sheet = workbook[sheet_name]
        # 找到要追加数据的起始单元格（例如，A2）
        start_cell_result = sheet.cell(row=start_row, column=start_col)
        # 追加数据到工作表
        for idx, value in enumerate(result_list, start=1):
            start_cell_result.offset(row=idx - 1).value = value
            # 保存工作簿
        workbook.save(self.__CASE_PATH)

    @classmethod
    def close_caseFile(cls):
        """
        Close case file
        """
        excel = win32.Dispatch("Excel.Application")
        # 检查Excel是否正在运行
        if excel.Application.Workbooks.Count > 0:
            for wb in excel.Application.Workbooks:
                if wb.FullName == cls.__CASE_PATH:
                    # 尝试关闭工作簿，可能会提示保存更改
                    wb.Close(SaveChanges=True)  # SaveChanges=False 表示不保存更改
                    # break
                    raise ApplicationException("close the case file error.")
        excel.Application.Quit()

    @staticmethod
    def clear_overthrew_logs(path='log'):
        # 设置路径
        folder_path = path
        if not os.listdir(folder_path):
            return
            # 获取当前日期，并计算3天前的日期
        current_date = datetime.now()
        threshold_date = current_date - timedelta(days=3)

        # 遍历文件夹
        for folder_name in os.listdir(folder_path):
            folder_full_path = os.path.join(folder_path, folder_name)
            # 检查是否是文件夹
            if os.path.isdir(folder_full_path):
                try:
                    # 尝试将文件夹名解析为日期
                    folder_date = datetime.strptime(folder_name, "%Y_%m_%d_%H-%M-%S")
                    # 比较日期，如果早于3天前，则删除
                    if folder_date < threshold_date:
                        print(f"正在清除超出3天的log文件夹: {folder_name}")
                        shutil.rmtree(folder_full_path)  # 删除文件夹
                except ValueError:
                    # 如果文件夹名不是日期格式，则跳过
                    print(f"跳过非日期格式文件夹: {folder_name}")

    @staticmethod
    def resource_backup(src_dir='resources', dest_dir=GetLog.log_path, dirs_to_clear=['image', 'pdf'],
                        case_name='case.xlsx'):
        # 确保目标目录存在
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        shutil.copy2(os.path.join(src_dir, case_name), os.path.join(dest_dir, case_name))
        # 加载Excel文件
        wb = openpyxl.load_workbook(os.path.join(src_dir, case_name))
        ws = wb.active
        # 遍历工作表中的所有行，从最后一行到第2行
        for row in range(ws.max_row, 1, -1):
            ws.delete_rows(row)
        wb.save(os.path.join(src_dir, case_name))
        # 清空指定目录
        for dir_name in dirs_to_clear:
            src_sub_dir = os.path.join(src_dir, dir_name)
            dest_sub_dir = os.path.join(dest_dir, dir_name)
            # 复制文件夹内容及其结构
            if os.path.exists(src_sub_dir):
                try:
                    # 使用移动操作代替复制和清空
                    shutil.move(src_sub_dir, dest_sub_dir)
                    print(f"Backup {src_sub_dir} to {dest_sub_dir}")
                    os.mkdir(src_sub_dir)
                except Exception as e:
                    raise ApplicationException(f"Failed to backup {src_sub_dir} to {dest_sub_dir}. Reason: {e}")
                m_logger.info(f"Cleared {src_sub_dir}")
