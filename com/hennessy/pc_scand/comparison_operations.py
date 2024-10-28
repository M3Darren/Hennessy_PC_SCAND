from com.hennessy.pc_scand.size_parameters import PaperSize


class ComparisonOperations:
    main_obj = {}

    bit_depth_obj = {'RGB': 24, '灰阶': 16, '黑白': 8}

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
        print(error_min, error_max, self.main_obj['w/h'][w_h_value], exception_value)
        return error_min <= self.main_obj['w/h'][w_h_value] <= error_max

    def compare_dpi(self):
        if self.main_obj['actual_dpi'][0] != self.main_obj['actual_dpi'][1] or self.main_obj['actual_dpi'][0] != \
                self.main_obj['dpi'] * self.main_obj['scaling']:
            return False
        else:
            return True

    def compare_main(self, obj):
        self.main_obj = obj
        if self.bit_depth_check() and self.width_and_height_check() and self.compare_dpi():
            return 'Pass'
        else:
            return 'Fail'


if __name__ == '__main__':
    print(9900.378 <= 440 <= 9960.378)
