from com.hennessy.pc_scand.io_operations import IoOperations
from com.hennessy.pc_scand.comparison_operations import ComparisonOperations


class ApplicationMain:
    result_list = []

    def __init__(self):
        self.case_info = None
        self.image_info = None
        self.io_obj = IoOperations()
        self.compare_obj = ComparisonOperations()

    def main(self):
        for idx, val in enumerate(self.io_obj.associated_list):
            result = self.result_conversion(self.merge_obj(val, idx))
            self.case_info[idx]['result'] = result
            self.result_list.append(result)
            # print(result)
        self.io_obj.write_to_excel_result(self.result_list)
        # print(self.result_list)

    def merge_obj(self, associated_obj, idx):
        self.image_info = self.io_obj.image_info_list
        self.case_info = self.io_obj.case_dict_list

        if isinstance(associated_obj, tuple):
            status = [None] * len(associated_obj)
            for idx, val in enumerate(associated_obj):
                m_obj = {**self.image_info[val], **self.case_info[idx]}
                # 进行比较，并且判断双面为true
                status[idx] = self.compare_obj.compare_main(m_obj)
                # print(m_obj)
            if status[0] and status[1]:
                return True
            else:
                return False
        else:
            # 非双面
            m_obj = {**self.image_info[associated_obj], **self.case_info[idx]}
            return self.compare_obj.compare_main(m_obj)

    def result_conversion(self, r_bool):
        if r_bool:
            return "Pass"
        else:
            return "Fail"


if __name__ == '__main__':
    app = ApplicationMain()
    app.main()
