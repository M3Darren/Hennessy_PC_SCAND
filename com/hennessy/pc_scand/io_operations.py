import io
import os

import fitz
import openpyxl
import pandas as pd
from PIL import Image
import win32com.client as win32
from openpyxl.drawing.image import Image as ImageRead
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.hyperlink import Hyperlink


class IoOperations:
    image_info_list = []
    case_dict_list = []
    folder_path = './images'

    def __init__(self):
        print("Reading images...")
        self.read_image()
        print("Reading case...")
        self.read_case()
        self.case_scaling_cleaning()
        self.merge_data_objects(self.image_info_list, self.case_dict_list)
        self.close_excel_workbook('./case.xlsx')
        for item in self.case_dict_list:
            print(item)

    def read_case(self):
        file_path = './case.xlsx'
        df = pd.read_excel(file_path, sheet_name=0)
        self.case_dict_list = df.to_dict(orient='records')

        # 打印转换后的数据（以字典列表为例）
        # for item in self.case_dict_list:
        #     print(item)

    def case_scaling_cleaning(self):
        # 遍历数据列表
        for item in self.case_dict_list:
            # # 使用split方法分割scaling值
            # parts = item['scaling'].split(':')
            # if len(parts) == 2:  # 确保分割后有两个部分
            # 提取数字部分并转换为整数
            # item['scaling'] = int(parts[1])
            item['scaling'] = int(item['scaling'].minute)

    def merge_data_objects(self, dict_list1, dict_list2):
        # 产生新列表
        # merged_list = [{**dict1, **dict2} for dict1, dict2 in zip(list1, list2)]
        # 不产生新列表
        # 确保两个列表长度相同
        if len(dict_list1) == len(dict_list2):
            # 遍历列表并合并对应位置的字典
            for i in range(len(dict_list1)):
                # 使用字典解包来合并，注意这会修改list1中的字典
                dict_list2[i] = {**dict_list1[i], **dict_list2[i]}

    def read_image(self):
        # 遍历文件夹中的所有文件
        for filename in sorted(os.listdir(self.folder_path)):
            # 检查文件是否为图片格式（比如jpg或png）
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                # 获取图片的完整路径
                file_path = os.path.join(self.folder_path, filename)

                # 打开图片
                with Image.open(file_path) as img:
                    # 获取图片的宽度和高度
                    width, height = img.size
                    # 获取位深度
                    depth = img.mode
                    # 获取DPI（如果不存在则返回默认的(72, 72)）
                    dpi = img.info.get('dpi', 'none')

                    # 保存图片信息
                    image_info = {
                        'filename': filename,
                        'w/h': (width, height),
                        'actual_dpi': dpi,
                        'actual_bit_depth': depth,
                        'result': ''
                    }

                    # 将信息添加到列表中
                    self.image_info_list.append(image_info)

                    # 输出每张图片的信息
        #             print(f"图片: {filename}, 宽度: {width}px, 高度: {height}px, DPI: {dpi}")
        # print(self.image_info_list)

    def read_pdf(self):
        # 打开PDF文件
        pdf_path = "./pdf/a5.pdf"
        doc = fitz.open(pdf_path)

        # 遍历PDF中的每一页
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            images = page.get_images(full=True)  # 获取页面中的所有图像

            for img_index, img in enumerate(images):
                xref = img[0]  # 图像的引用
                base_image = doc.extract_image(xref)  # 提取图像为字节数据
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]  # 图像扩展名

                # 使用Pillow打开图像
                with Image.open(io.BytesIO(image_bytes)) as pil_image:
                    try:
                        dpi = pil_image.info.get("dpi")  # 尝试获取DPI
                        if dpi:
                            print(f"Page {page_num + 1}, Image {img_index + 1}: DPI = {dpi}")
                        else:
                            print(f"Page {page_num + 1}, Image {img_index + 1}: DPI not available")

                            # 获取图像的尺寸（宽度，高度）
                        width, height = pil_image.size
                        print(f"Size: {width}x{height}")

                        # 这里你可以添加逻辑来验证缩放比
                        # 你需要知道原始图像的尺寸来进行比较

                    except Exception as e:
                        print(f"Error processing image on page {page_num + 1}, index {img_index + 1}: {e}")

    def write_to_excel_result(self, result_list):
        # 假设您的Excel文件名为'existing_file.xlsx'，并且您希望将数据追加到Sheet1的A列下方
        file_path = './case.xlsx'
        sheet_name = 'Sheet1'
        start_row = 2  # 假设从第2行开始追加（第1行通常是标题行）
        start_col = 5  # A列的列号

        # 打开已存在的Excel文件
        workbook = openpyxl.load_workbook(file_path)

        # 选择工作表
        sheet = workbook[sheet_name]

        # 找到要追加数据的起始单元格（例如，A2）
        start_cell_result = sheet.cell(row=start_row, column=start_col)

        # 追加数据到工作表
        for idx, value in enumerate(result_list, start=1):
            start_cell_result.offset(row=idx - 1).value = value

            # 保存工作簿
        workbook.save(file_path)

    def write_to_excel_image(self):
        start_col = 6
        # 假设您的Excel文件名为'existing_file.xlsx'，并且您希望将数据追加到Sheet1的A列下方
        file_path = './1.xlsx'
        sheet_name = 'Sheet1'
        start_row = 2  # 假设从第2行开始追加（第1行通常是标题行）

        # 打开已存在的Excel文件
        workbook = openpyxl.load_workbook(file_path)

        # 选择工作表
        sheet = workbook[sheet_name]
        # 假设你的图片文件位于当前目录下的"images"文件夹中
        image_folder = "images/"

        # 遍历图片文件，并在Excel中插入链接
        row_num = 1
        for image_name in ["a5-wifi-200-24bit.1.jpg", "a5-wifi-200-24bit.2.jpg"]:  # 替换为你的图片文件名
            image_path = image_folder + image_name

            # 在Excel中插入图片名称
            sheet.cell(row=row_num, column=1, value=image_name)

            # 创建一个指向图片文件的超链接
            hyperlink = Hyperlink(ref=f"{get_column_letter(1)}{row_num}", target=image_path, location="",
                                  tooltip="Open Image")
            sheet._hyperlink(hyperlink)

            # 移动到下一行
            row_num += 1

            # 保存工作簿
        workbook.save(file_path)

    def close_excel_workbook(self, file_path):
        excel = win32.Dispatch("Excel.Application")
        try:
            # 检查Excel是否正在运行
            if excel.Application.Workbooks.Count > 0:
                for wb in excel.Application.Workbooks:
                    if wb.FullName == file_path:
                        # 尝试关闭工作簿，可能会提示保存更改
                        wb.Close(SaveChanges=False)  # SaveChanges=False 表示不保存更改
                        break
        except Exception as e:
            print(f"Error closing workbook: {e}")
        finally:
            # 尝试退出Excel应用程序（如果它是空的，则不会真正关闭）
            print("Exiting Excel application...")
            excel.Application.Quit()


if __name__ == '__main__':
    io_obj = IoOperations()
