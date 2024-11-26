import queue

import cv2
import imagehash
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim
from file_exception import FileReadException
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
    _remarks_list = queue.Queue()

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
            self._remarks_list.put(bit_depth_str)
            return False
        else:
            return True

    def color_mode_verification(self):
        """
        比较图片的色彩模式
        """
        m_logger.info('------ [ color_mode_verification ] ------')
        image_array = np.array(self.__merge_objects['pil_image_obj'])
        m_logger.info(f"image_array:{image_array}")

        def get_color_mode(img_obj):

            if len(img_obj.shape) == 2:  # 判断为灰阶
                parts = self.__merge_objects['filename'].rsplit('.', 1)

                if len(parts) > 1:
                    if parts[1] == 'jpg' or parts[1] == 'jpeg':
                        return self.__color_mode_conversion[0]
                return self.__color_mode_conversion[1]
            elif len(img_obj.shape) == 3:
                b, g, r = cv2.split(img_obj)
                if (abs(b - g) <= 5).all() and (abs(g - r) <= 5).all():
                    parts = self.__merge_objects['filename'].rsplit('.', 1)

                    if len(parts) > 1:
                        if parts[1] == 'jpg' or parts[1] == 'jpeg':
                            return self.__color_mode_conversion[0]
                    unique_vals = np.unique(b)
                    if set(unique_vals).issubset({0, 1, 2, 3, 4, 250, 251, 252, 253, 254, 255}):  # 判断为黑白
                        return self.__color_mode_conversion[0]
                    return self.__color_mode_conversion[1]
                else:  # 判断为彩色
                    return self.__color_mode_conversion[2]
            else:
                return "Unknown type"

        # if _backup_flag:
        #     m_logger.info(f'{image_array}')
        color_mode_str = f"actual_color_mode:{get_color_mode(image_array)} & excepted:{self.__merge_objects.get(_case_expected_color_mode)}"
        m_logger.info(color_mode_str)
        if get_color_mode(image_array) == self.__merge_objects.get(_case_expected_color_mode):
            return True
        else:
            del self.__merge_objects['pil_image_obj']
            self._remarks_list.put(f"({self.__merge_objects['filename']})" + color_mode_str)
            return False

    def dpi_check(self):
        """
        比较图片的dpi,返回boolean值
        """
        if self.__merge_objects['model']:
            return True
        m_logger.info('------ [ dpi_check ] ------')
        m_logger.info(
            f"actual_dpi：{self.__merge_objects.get('actual_dpi')} & expected_dpi：{self.__merge_objects.get(_case_expected_dpi)}")
        if self.__merge_objects.get('actual_dpi')[0] != self.__merge_objects.get('actual_dpi')[1] or \
                self.__merge_objects.get('actual_dpi')[0] != self.__merge_objects.get(
            _case_expected_dpi) * self.__merge_objects.get(_case_scaling_ratio):
            dpi_str = "'dpi' - Actual results did not meet expectations"
            m_logger.warn(dpi_str)
            self._remarks_list.put(dpi_str)
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
            if not self.calculate_width_height_error_range(0):
                w_h_str = "@@@ Width @@@ - Actual results did not meet expectations"

            else:
                w_h_str = "@@@ Height @@@ - Actual results did not meet expectations"
            m_logger.warn(w_h_str)
            self._remarks_list.put(w_h_str)
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
            f"{wh} = = = > (actual_val:{self.__merge_objects['w_h'][w_or_h_val]}，expected_val:{int(exception_value)})")
        m_logger.info(f'difference in {l_t} and {r_b} {wh}：{difference_value}')
        return difference_value <= LoadConfig.load_yaml_error_range()[w_or_h_val] * 2

    def similarity_calculation(self, page_index):
        """
        计算相似度
        """
        m_logger.info('------ [ similarity_calculation ] ------')

        ref_path = LoadConfig.load_yaml_resources_path("reference_path") + '/' + self.__merge_objects[
            _case_paper_size] + page_index + "_ref.jpg"
        # if not os.path.exists(ref_path):
        #     raise FileNotFoundException(ref_path)
        # if self.__merge_objects[_case_scanning_mode] == 1:
        #     return self.similarity_SSIM(ref_path)
        # else:
        #     return self.similarity_wHash(ref_path)
        return self.similarity_pHash(ref_path)

    def similarity_pHash(self, ref_path):

        # 生成图像的感知哈希
        try:
            hash1 = imagehash.phash(self.__merge_objects['pil_image_obj'])
            hash2 = imagehash.phash(Image.open(ref_path))
            del self.__merge_objects['pil_image_obj']
        except Exception as e:
            raise FileReadException
        # 计算相似度
        similarity = 1 - (hash1 - hash2) / len(hash1.hash)  # 范围为0到1，值越大表示相似度越高
        m_logger.info(f'ref_file：{ref_path}')
        if similarity >= 0.25:
            m_logger.info(f"image high similarity @@@@@@@@@@@@@@########  whash：{similarity}")
            return True
        else:
            m_logger.warn(f"low similarity - - > whash：{similarity}")
            self._remarks_list.put(f"({self.__merge_objects['filename']})low similarity")
            return False

    def similarity_SSIM(self, ref_path):
        # 将 PIL 图像对象转换为灰度 NumPy 数组
        img1 = np.array(self.__merge_objects['pil_image_obj'].convert('L'))  # 转换为灰度图
        img2 = cv2.imread(ref_path, cv2.IMREAD_GRAYSCALE)

        # 调整较小的图像大小以匹配较大的图像
        img2_resized = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        # 计算 SSIM
        score, _ = ssim(img1, img2_resized, full=True)
        del self.__merge_objects['pil_image_obj']
        if round(score, 3) >= 0.460:
            m_logger.info(f"image high similarity @@@@@@@@@@@@@@########  SSIM：{round(score, 3)}")
            return True
        else:
            m_logger.warn(f"low similarity - - > SSIM：{round(score, 3)}")
            self._remarks_list.put("low similarity")
            return False

    def compare_main(self, objs, **double_sided_index):
        """
        主比较函数
        """
        page_index = double_sided_index.get('page_index', '')
        m_logger.info(f'@########@ Compare：{objs["filename"]}--------------------------------')
        self.__merge_objects = objs
        if self.dpi_check() and self.color_mode_verification() and self.width_height_pixel_check() and self.similarity_calculation(
                str(page_index)):
            return True
        else:
            return False
