from com.hennessy.pc_scand.size_parameters import PaperSize
import imagehash
from PIL import Image


class ComparisonOperations:
    main_obj = {}

    bit_depth_obj = {'RGB': 24, '灰阶': 8, '黑白': 1}

    def bit_depth_check(self):

        if self.bit_depth_obj[self.main_obj['actual_bit_depth']] != self.main_obj['except_bit_depth']:
            return False
        else:
            return True

    def width_and_height_check(self):
        if self.error_judging(0) and self.error_judging(1):
            return True
        else:
            return False

    def error_judging(self, w_h_value):
        error_value = 0.07874 * self.main_obj['dpi'] / self.main_obj['scaling']
        exception_value = self.main_obj['dpi'] * PaperSize.get_size(self.main_obj['size'])[
            w_h_value] / self.main_obj['scaling']
        error_min = exception_value - error_value
        error_max = exception_value + error_value
        print(
            f"{w_h_value}===最小误差:{error_min}, 最大误差:{error_max}, 实际值:{self.main_obj['w/h'][w_h_value]},预期值:{exception_value}")
        return error_min <= self.main_obj['w/h'][w_h_value] <= error_max

    def compare_dpi(self):
        if self.main_obj['actual_dpi'][0] != self.main_obj['actual_dpi'][1] or self.main_obj['actual_dpi'][0] != \
                self.main_obj['dpi'] * self.main_obj['scaling']:
            return False
        else:
            return True

    def compare_image(self):
        REFERENCE_IMAGE_PATH = "./images/reference_image"
        path1 = "./images" / self.main_obj['filename']
        path2 = REFERENCE_IMAGE_PATH / self.main_obj['size'] + "_ref.jpg"
        # 生成图像的感知哈希
        hash1 = imagehash.whash(Image.open(path1))
        hash2 = imagehash.whash(Image.open(path2))
        # 计算相似度
        similarity = 1 - (hash1 - hash2) / len(hash1.hash)  # 范围为0到1，值越大表示相似度越高

        print(f"whash：{similarity}")
        if similarity == 1:
            return True
        else:
            return False

    def compare_main(self, obj):
        self.main_obj = obj
        if self.bit_depth_check() and self.compare_dpi() and self.width_and_height_check() and self.compare_image():
            return True
        else:
            return False
