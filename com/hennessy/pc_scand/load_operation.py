import io
import os
import queue
import win32com.client as win32
import fitz
import openpyxl
import pandas as pd
from PIL import Image

from com.hennessy.pc_scand.load_yaml_config import LoadConfig


class LoadOperation:
    """
    LoadOperation class
    """
    _case_queue = queue.Queue()
    __image_queue = queue.Queue()
    __pdf_queue = queue.Queue()
    _merge_queue = queue.Queue()
    __CASE_PATH = LoadConfig.load_yaml_path("case_path")
    __IMAGE_PATH = LoadConfig.load_yaml_path("image_path")
    __PDF_PATH = LoadConfig.load_yaml_path("pdf_path")

    def __init__(self):
        """
        Constructor
        """
        print("read case ...")
        self.load_case_and_convert()
        print("read image ...")
        self.load_image()
        print("read pdf ...")
        self.load_pdf()
        print("merge data ...")
        self.constructive_load_data()
        print("merged Data : >>>>>>>>>>>>>>>>")
        self.iterator(self._merge_queue)

    def iterator(self, obj):
        for item in obj.queue:
            print(item)

    def load_case_and_convert(self):
        """
        Load case and converter.
        """
        df = pd.read_excel(self.__CASE_PATH, sheet_name=0)
        for row in df.to_dict(orient='records'):
            scaling_str = row['scaling']
            if not isinstance(scaling_str, str):
                scaling_str = scaling_str.strftime("%H:%M")
            row['scaling'] = int(scaling_str[-1])
            if row['scand_way'] == "输稿器（双面）":
                row['scand_way'] = 1
            if row['preservation_method'] == "PDF":
                row['preservation_method'] = 1
            self._case_queue.put(row)

    def load_image(self):
        """
        Load image
        """
        for filename in sorted(os.listdir(self.__IMAGE_PATH)):
            # 检查文件是否为图片格式（比如jpg或png）
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                # 获取图片的完整路径
                file_path = os.path.join(self.__IMAGE_PATH, filename)
                # 打开图片
                img = Image.open(file_path)

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
        for filename in sorted(os.listdir(self.__PDF_PATH)):
            # 检查文件是否为图片格式（比如jpg或png）
            if filename.lower().endswith('pdf'):
                # 获取图片的完整路径
                pdf_path = os.path.join(self.__PDF_PATH, filename)
                # 打开PDF文件
                doc = fitz.open(pdf_path)
                # 遍历PDF中的每一页
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    images = page.get_images(full=True)  # 获取页面中的所有图像
                    for img_index, img in enumerate(images):
                        xref = img[0]  # 图像的引用
                        base_image = doc.extract_image(xref)  # 提取图像为字节数据
                        image_bytes = base_image["image"]
                        # 使用Pillow打开图像
                        pil_image = Image.open(io.BytesIO(image_bytes))

                        try:
                            depth = pil_image.mode
                            dpi = pil_image.info.get("dpi")  # 尝试获取DPI
                            # 获取图像的尺寸（宽度，高度）
                            width, height = pil_image.size
                            pdf_info = {
                                'filename': filename + '_' + str(page_num + 1),
                                'w_h': (width, height),
                                'actual_dpi': dpi,
                                'actual_bit_depth': depth,
                                'result': '',
                                'pil_image_obj': pil_image
                            }
                            self.__pdf_queue.put(pdf_info)
                        except Exception as e:
                            print(f"Error processing image on page {page_num + 1}, index {img_index + 1}: {e}")

    def constructive_load_data(self):
        """
        Merge load data
        """
        for case_item in self._case_queue.queue:
            if case_item['preservation_method'] == 1:
                if case_item['scand_way'] == 1:
                    self._merge_queue.put((self.__pdf_queue.get(), self.__pdf_queue.get()))
                else:
                    self._merge_queue.put(self.__pdf_queue.get())

            else:
                if case_item['scand_way'] == 1:
                    self._merge_queue.put((self.__image_queue.get(), self.__image_queue.get()))
                else:
                    self._merge_queue.put(self.__image_queue.get())

    def write_to_caseFile_result(self, result_list):
        sheet_name = 'Case'
        start_row = 2  # 假设从第2行开始追加（第1行通常是标题行）
        start_col = 7  # A列的列号
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

    def close_caseFile(self):
        """
        Close case file
        """
        excel = win32.Dispatch("Excel.Application")
        try:
            # 检查Excel是否正在运行
            if excel.Application.Workbooks.Count > 0:
                for wb in excel.Application.Workbooks:
                    if wb.FullName == self.__CASE_PATH:
                        # 尝试关闭工作簿，可能会提示保存更改
                        wb.Close(SaveChanges=True)  # SaveChanges=False 表示不保存更改
                        break
        except Exception as e:
            print(f"Error closing workbook: {e}")
        finally:
            # 尝试退出Excel应用程序（如果它是空的，则不会真正关闭）
            print("Exiting Excel application...")
            excel.Application.Quit()

# LoadOperation()
