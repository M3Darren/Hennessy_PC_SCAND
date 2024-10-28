from com.hennessy.pc_scand.io_operations import IoOperations
from com.hennessy.pc_scand.comparison_operations import ComparisonOperations


class ApplicationMain:
    result_list = []

    def __init__(self):
        self.io_obj = IoOperations()
        self.compare_obj = ComparisonOperations()

    def main(self):
        for image_info in self.io_obj.image_info_list:
            image_info['result'] = self.compare_obj.compare_main(image_info)
            self.result_list.append(image_info['result'])
            print(image_info)
        self.io_obj.write_to_excel_result(self.result_list)
        print(self.result_list)


if __name__ == '__main__':
    app = ApplicationMain()
    app.main()
