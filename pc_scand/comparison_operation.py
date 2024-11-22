import os

import cv2
import imagehash
import numpy as np
from PIL import Image

from file_exception import FileNotFoundException, FileReadException
from get_log import m_logger
from load_yaml_config import LoadConfig, _case_expected_bit_depth, _case_expected_dpi, \
    _case_scaling_ratio, _case_paper_size, _case_expected_color_mode
from paper_size import PaperSize


class ComparisonOperation:
    """
    @Author: M3Darren
    @Described: 比较操作,接收传入的合并对象
    """

    __merge_objects = {}
    __bit_depth_conversion = {'RGB': 24, '灰阶': 8, '黑白': 1}
    __color_mode_conversion = ('黑白', '灰阶', '彩色')
    _remarks_list = []

    def __init__(self):
        """
        Constructor
        """
        m_logger.info("ComparisonOperation Constructor")

    def bit_depth_check(self):
        """
        比较图片的bit深度,返回boolean值
        """
        m_logger.info('------ [ bit_depth_check ] ------')
        m_logger.info(
            f"actual_bit_depth：{self.__bit_depth_conversion.get(self.__merge_objects.get('actual_bit_depth'))} & "
            f"expected_bit_depth：{self.__merge_objects.get(_case_expected_bit_depth)}")
        if self.__bit_depth_conversion.get(self.__merge_objects.get('actual_bit_depth')) != int(
                self.__merge_objects.get(_case_expected_bit_depth)):
            bit_depth_str = "'bit_depth' - Actual results did not meet expectations"
            m_logger.warn(bit_depth_str)
            self._remarks_list.append(bit_depth_str)
            return False
        else:
            return True

    def color_mode_verification(self):
        """
        比较图片的色彩模式
        """
        m_logger.info('------ [ color_mode_verification ] ------')
        image_array = np.array(self.__merge_objects['pil_image_obj'])

        def get_color_mode(img_obj):
            if len(img_obj.shape) == 2:  # 判断为灰阶
                return self.__color_mode_conversion[1]
            elif len(img_obj.shape) == 3:
                b, g, r = cv2.split(img_obj)

                if (abs(b - g) <= 1).all() and (abs(g - r) <= 1).all():
                    unique_vals = np.unique(b)
                    if set(unique_vals).issubset({0, 1, 254, 255}):  # 判断为黑白
                        return self.__color_mode_conversion[0]
                    return self.__color_mode_conversion[1]
                else:  # 判断为彩色
                    return self.__color_mode_conversion[2]
            else:
                return "Unknown type"

        color_mode_str = f"actual_color_mode:{get_color_mode(image_array)} & excepted:{self.__merge_objects.get(_case_expected_color_mode)}"
        m_logger.info(color_mode_str)
        self._remarks_list.append(color_mode_str)
        return get_color_mode(image_array) == self.__merge_objects.get(_case_expected_color_mode)

    def dpi_check(self):
        """
        比较图片的dpi,返回boolean值
        """
        m_logger.info('------ [ dpi_check ] ------')
        m_logger.info(
            f"actual_dpi：{self.__merge_objects.get('actual_dpi')} & expected_dpi：{self.__merge_objects.get(_case_expected_dpi)}")
        if self.__merge_objects.get('actual_dpi')[0] != self.__merge_objects.get('actual_dpi')[1] or \
                self.__merge_objects.get('actual_dpi')[0] != self.__merge_objects.get(
            _case_expected_dpi) * self.__merge_objects.get(_case_scaling_ratio):
            dpi_str = "'dpi' - Actual results did not meet expectations"
            m_logger.warn(dpi_str)
            self._remarks_list.append(dpi_str)
            return False
        else:
            return True

    def width_height_pixel_check(self):
        """
        比较图片的宽高像素,返回boolean值
        """
        m_logger.info('------ [ width_height_pixel_check ] ------')

        if self.calculate_width_height_error_range(0) and self.calculate_width_height_error_range(1):
            return True
        else:
            if self.calculate_width_height_error_range(0):
                width_str = "@@@ Width @@@ - Actual results did not meet expectations"
                m_logger.warn(width_str)
                self._remarks_list.append(width_str)
            else:
                height_str = "@@@ Height @@@ - Actual results did not meet expectations"
                m_logger.warn(height_str)
                self._remarks_list.append(height_str)
            return False

    def calculate_width_height_error_range(self, w_or_h_val):
        """
        计算宽高像素的误差
        """
        exception_value = self.__merge_objects[_case_expected_dpi] * \
                          (PaperSize.get_size(self.__merge_objects[_case_paper_size])[
                               w_or_h_val] / (self.__merge_objects[_case_scaling_ratio] * 25.4))
        difference_value = round(abs(exception_value - self.__merge_objects['w_h'][w_or_h_val]) * (
                25.4 / (self.__merge_objects[_case_expected_dpi] * self.__merge_objects[_case_scaling_ratio])), 3)
        if w_or_h_val:
            wh = "height"
            l_t = "top"
            r_b = "bottom"
        else:
            wh = "width"
            l_t = "left"
            r_b = "right"
        m_logger.info(
            f"{wh} = = = > (actual_val:{self.__merge_objects['w_h'][w_or_h_val]}，expected_val:{exception_value})")
        m_logger.info(f'difference in {l_t} and {r_b} {wh}：{difference_value}')

        return difference_value <= LoadConfig.load_yaml_error_range()[w_or_h_val] * 2

    def similarity_calculation(self, page_index):
        """
        计算相似度
        """
        m_logger.info('------ [ similarity_calculation ] ------')

        ref_path = LoadConfig.load_yaml_resources_path("reference_path") + '/' + self.__merge_objects[
            _case_paper_size] + page_index + "_ref.jpg"
        if not os.path.exists(ref_path):
            raise FileNotFoundException(ref_path)
        # 生成图像的感知哈希
        try:
            hash1 = imagehash.whash(self.__merge_objects['pil_image_obj'])
            hash2 = imagehash.whash(Image.open(ref_path))
            self.__merge_objects['pil_image_obj'].close()
        except Exception as e:
            raise FileReadException
        # 计算相似度
        similarity = 1 - (hash1 - hash2) / len(hash1.hash)  # 范围为0到1，值越大表示相似度越高
        m_logger.info(f'ref_file：{ref_path}')
        if similarity > 0.7:
            m_logger.info(f"image high similarity @@@@@@@@@@@@@@########  whash：{similarity}")
            return True
        else:
            m_logger.warn(f"low similarity - - > whash：{similarity}")
            self._remarks_list.append("low similarity")
            return False

    def compare_main(self, objs, **double_sided_index):
        """
        主比较函数
        """
        page_index = double_sided_index.get('page_index', '')
        m_logger.info(f'@########@ Compare：{objs["filename"]}--------------------------------')
        self.__merge_objects = objs
        if self.color_mode_verification() and self.dpi_check() and self.width_height_pixel_check() and self.similarity_calculation(
                str(page_index)):
            return True
        else:
            return False
