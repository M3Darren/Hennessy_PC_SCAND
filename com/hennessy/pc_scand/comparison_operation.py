import os

import imagehash
from PIL import Image

from com.hennessy.pc_scand.file_exception import FileNotFoundException, FileReadException
from com.hennessy.pc_scand.get_log import m_logger
from com.hennessy.pc_scand.load_yaml_config import LoadConfig, _case_expected_bit_depth, _case_expected_dpi, \
    _case_scaling_ratio, _case_paper_size
from com.hennessy.pc_scand.paper_size import PaperSize


class ComparisonOperation:
    """
    @Author: M3Darren
    @Described: 比较操作,接收传入的合并对象
    """
    __error_range_val = round(LoadConfig.load_yaml_error_range() / 25.4, 5)
    __merge_objects = {}
    __bit_depth_conversion = {'RGB': 24, '灰阶': 8, '黑白': 1}

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
            f"actual_bit_depth：{self.__bit_depth_conversion.get(self.__merge_objects.get('actual_bit_depth'))} & expected_bit_depth：{self.__merge_objects.get(_case_expected_bit_depth)}")
        if self.__bit_depth_conversion.get(self.__merge_objects.get('actual_bit_depth')) != int(
                self.__merge_objects.get(_case_expected_bit_depth)):
            m_logger.warn("'bit_depth' Actual results did not meet expectations")
            return False
        else:
            return True

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
            m_logger.warn("'dpi' Actual results did not meet expectations")
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
            m_logger.warn("'width_height' Actual results did not meet expectations")
            return False

    def calculate_width_height_error_range(self, w_or_h_val):
        """
        计算宽高像素的误差范围
        """
        error_value = self.__error_range_val * self.__merge_objects[_case_expected_dpi] / self.__merge_objects[
            _case_scaling_ratio]
        exception_value = self.__merge_objects[_case_expected_dpi] * \
                          PaperSize.get_size(self.__merge_objects[_case_paper_size])[
                              w_or_h_val] / self.__merge_objects[_case_scaling_ratio]
        error_min = exception_value - error_value
        error_max = exception_value + error_value
        wh = None
        if w_or_h_val:
            wh = "height"
        else:
            wh = "width"
        m_logger.info(
            f"{wh} = = = > min_error_range：{error_min}，max_error_range)：{error_max}，actual_val:{self.__merge_objects['w_h'][w_or_h_val]}，expected_val:{exception_value}")

        return error_min <= self.__merge_objects['w_h'][w_or_h_val] <= error_max

    def similarity_calculation(self):
        """
        计算相似度
        """
        m_logger.info('------ [ similarity_calculation ] ------')

        ref_path = LoadConfig.load_yaml_resources_path("reference_path") + '/' + self.__merge_objects[
            _case_paper_size] + "_ref.jpg"
        if not os.path.exists(ref_path):
            raise FileNotFoundException(ref_path)
        # 生成图像的感知哈希
        try:
            hash1 = imagehash.whash(self.__merge_objects['pil_image_obj'])
            hash2 = imagehash.whash(Image.open(ref_path))
        except Exception as e:
            raise FileReadException
        # 计算相似度
        similarity = 1 - (hash1 - hash2) / len(hash1.hash)  # 范围为0到1，值越大表示相似度越高

        if similarity == 1:
            m_logger.info(f"image high similarity")
            return True
        else:
            m_logger.warn(f"low similarity - - > whash：{similarity}")
            return False

    def compare_main(self, objs):
        """
        主比较函数
        """
        m_logger.info(f'@########@ Compare：{objs["filename"]}--------------------------------')
        self.__merge_objects = objs
        if self.bit_depth_check() and self.dpi_check() and self.width_height_pixel_check() and self.similarity_calculation():
            return True
        else:
            return False
