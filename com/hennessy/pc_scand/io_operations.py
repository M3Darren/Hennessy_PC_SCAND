import io
import os

import fitz
import openpyxl
import pandas as pd
from PIL import Image
import win32com.client as win32


class IoOperations:
    image_info_list = []
    pdf_info_list = []
    case_dict_list = []
    associated_list = []
    folder_path = './images'

    def __init__(self):
        print("Reading images...")
        self.read_image()
        print("Reading case...")
        self.read_case()
        self.read_pdf()
        self.case_scaling_cleaning()

        self.merge_associated_data()
        # self.close_excel_workbook('./case.xlsx')
        print(self.associated_list)
        for item in self.pdf_info_list:
            print(item)

    def read_case(self):
        file_path = './case.xlsx'
        df = pd.read_excel(file_path, sheet_name=0)
        self.case_dict_list = df.to_dict(orient='records')
        # self.associated_list = [None] * len(self.case_dict_list)

    def case_scaling_cleaning(self):
        # 遍历case数据列表
        for item in self.case_dict_list:
            item['scaling'] = int(item['scaling'].minute)
            if item['scand_way'] == "输稿器（双面）":
                item['scand_way'] = 1
            else:
                item['scand_way'] = 0
            if item['preservation_method'] == "PDF":
                item['preservation_method'] = 1
            else:
                item['preservation_method'] = 0

    def merge_associated_data(self):
        p_count = 0
        j_count = 0
        for idx, val in enumerate(self.case_dict_list):
            # [j0,(j1,j2),p0,j3,p5,(p6,p7)]
            if val['preservation_method']:  # pdf
                if val['scand_way']:
                    p_tuple = (p_count, p_count + 1)  # 这里可以直接写入图像数据
                    self.associated_list.append(p_tuple)
                else:
                    self.associated_list.append(p_count)
                p_count += 1
            else:  # jpg
                if val['scand_way']:
                    j_tuple = (j_count, j_count + 1)
                    self.associated_list.append(j_tuple)
                else:
                    self.associated_list.append(j_count)
                j_count += 1

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
        for filename in sorted(os.listdir('./pdf')):
            # 检查文件是否为图片格式（比如jpg或png）
            if filename.lower().endswith('pdf'):
                # 获取图片的完整路径
                pdf_path = os.path.join('./pdf', filename)
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
                        with Image.open(io.BytesIO(image_bytes)) as pil_image:
                            try:
                                depth = pil_image.mode
                                dpi = pil_image.info.get("dpi", "none")  # 尝试获取DPI
                                if dpi:
                                    print(f"Page {page_num + 1}, Image {img_index + 1}: DPI = {dpi}")
                                else:
                                    print(f"Page {page_num + 1}, Image {img_index + 1}: DPI not available")

                                    # 获取图像的尺寸（宽度，高度）
                                width, height = pil_image.size
                                pdf_info = {
                                    'filename': filename +'_'+ str(page_num + 1),
                                    'w/h': (width, height),
                                    'actual_dpi': dpi,
                                    'actual_bit_depth': depth,
                                    'result': ''
                                }
                                self.pdf_info_list.append(pdf_info)
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

    def close_excel_workbook(self, file_path):
        if self.is_excel_file_open(file_path):
            self.save_and_close_excel_file(file_path)
        else:
            print(f"Excel file {file_path} is not open.")

    def is_excel_file_open(self, file_path):
        excel = win32.Dispatch("Excel.Application")
        try:
            # 尝试访问Excel的Workbooks集合，这可能会因为Excel未运行而抛出异常
            workbooks = excel.Workbooks
            for workbook in workbooks:
                try:
                    # 尝试访问FullName属性，这可能会因为工作簿未保存或路径无法访问而抛出异常
                    if workbook.FullName == file_path:
                        return True
                except Exception:
                    # 忽略无法访问FullName属性的工作簿（可能是未保存的工作簿）
                    continue
            return False
        except Exception as e:
            # 如果无法访问Workbooks集合，可能是因为Excel没有运行
            print(f"Error accessing Excel Workbooks: {e}")
            return False
        finally:
            # 清理COM对象（可选，但推荐）
            # 注意：在这个例子中，我们不关闭Excel应用程序，因为我们只是检查它
            # 如果你打算在脚本结束时关闭Excel，你应该在finally块之外处理它
            del excel

    def save_and_close_excel_file(self, file_path):
        excel = win32.Dispatch("Excel.Application")
        try:
            workbooks = excel.Workbooks
            for workbook in workbooks:
                try:
                    if workbook.FullName == file_path:
                        workbook.Save()
                        workbook.Close(SaveChanges=True)
                        break  # 找到匹配的工作簿后退出循环
                except Exception as e:
                    print(f"Error accessing workbook {workbook.Name}: {e}")
                    # 如果无法访问某个工作簿，继续检查下一个
            else:
                # 如果没有找到匹配的工作簿，则打印消息（可选）
                print(f"Workbook with path {file_path} not found.")
        except Exception as e:
            print(f"Error accessing Excel: {e}")
        finally:
            # 如果Excel没有任何工作簿打开，或者我们关闭了所有工作簿，尝试退出Excel应用程序
            # 注意：如果Excel是由用户手动打开的，并且用户不希望它关闭，则下面的代码可能会干扰用户的工作流程
            try:
                if excel.Workbooks.Count == 0:
                    excel.Quit()
            except Exception as e:
                print(f"Error quitting Excel: {e}")
                # 清理COM对象
            del excel


if __name__ == '__main__':
    io = IoOperations()
