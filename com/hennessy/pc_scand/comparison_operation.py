import imagehash
from PIL import Image

from com.hennessy.pc_scand.load_yaml_config import LoadConfig
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
        print("ComparisonOperation Constructor")

    def bit_depth_check(self):
        """
        比较图片的bit深度,返回boolean值
        """

        if self.__bit_depth_conversion.get(self.__merge_objects.get('actual_bit_depth')) != int(
                self.__merge_objects.get(
                    'expected_bit_depth')):
            return False
        else:
            return True

    def dpi_check(self):
        """
        比较图片的dpi,返回boolean值
        """
        if self.__merge_objects.get('actual_dpi')[0] != self.__merge_objects.get('actual_dpi')[1] or \
                self.__merge_objects.get('actual_dpi')[0] != self.__merge_objects.get(
            'expected_dpi') * self.__merge_objects.get('scaling'):
            return False
        else:
            return True

    def width_height_pixel_check(self):
        """
        比较图片的宽高像素,返回boolean值
        """
        print('--------------------------------------------------')
        print(self.__merge_objects['filename'] + ' --------误差值：{}------------------------')
        if self.calculate_width_height_error_range(0) and self.calculate_width_height_error_range(1):
            return True
        else:
            return False

    def calculate_width_height_error_range(self, w_or_h_val):
        """
        计算宽高像素的误差范围
        """
        error_value = self.__error_range_val * self.__merge_objects['expected_dpi'] / self.__merge_objects['scaling']
        exception_value = self.__merge_objects['expected_dpi'] * PaperSize.get_size(self.__merge_objects['size'])[
            w_or_h_val] / self.__merge_objects['scaling']
        error_min = exception_value - error_value
        error_max = exception_value + error_value
        wh = None
        if w_or_h_val:
            wh = "高"
        else:
            wh = "宽"
        print(
            f"{wh} = = = > 最小误差:{error_min}, 最大误差:{error_max}, 实际值:{self.__merge_objects['w_h'][w_or_h_val]},预期值:{exception_value}")

        return error_min <= self.__merge_objects['w_h'][w_or_h_val] <= error_max

    def similarity_calculation(self):
        """
        计算相似度
        """

        ref_path = LoadConfig.load_yaml_path("reference_path") + '/' + self.__merge_objects['size'] + "_ref.jpg"
        # 生成图像的感知哈希
        hash1 = imagehash.whash(self.__merge_objects['pil_image_obj'])
        hash2 = imagehash.whash(Image.open(ref_path))
        # 计算相似度
        similarity = 1 - (hash1 - hash2) / len(hash1.hash)  # 范围为0到1，值越大表示相似度越高
        print(f"whash：{similarity}")
        if similarity == 1:
            return True
        else:
            return False

    def compare_main(self, objs):
        """
        主比较函数
        """
        self.__merge_objects = objs
        if self.bit_depth_check() and self.dpi_check() and self.width_height_pixel_check() and self.similarity_calculation():
            return True
        else:
            return False
