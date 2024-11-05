from com.hennessy.pc_scand.comparison_operation import ComparisonOperation
from com.hennessy.pc_scand.load_operation import LoadOperation


class Application:
    __load_operation = None
    __comparison_operation = None
    __merge_objs = None
    __case_objs = None
    __result_list = []

    def __init__(self):
        self.__load_operation = LoadOperation()
        self.__comparison_operation = ComparisonOperation()
        self.__merge_objs = self.__load_operation._merge_queue
        self.__case_objs = self.__load_operation._case_queue.queue

    def main(self):
        print("compare loading...")
        for case in self.__case_objs:
            result = self.deconstructing_obj(self.__merge_objs.get(), case)
            case['result'] = self.result_converted(result)
            self.__result_list.append(case['result'])

        self.__load_operation.write_to_caseFile_result(self.__result_list)

    def deconstructing_obj(self, merge_objs, case_obj):
        if isinstance(merge_objs, tuple):
            double_sided_flag = True
            for obj in merge_objs:
                double_sided_flag = self.__comparison_operation.compare_main({**obj, **case_obj})
                if not double_sided_flag:
                    double_sided_flag = False
                    break
            return double_sided_flag
        else:
            return self.__comparison_operation.compare_main({**merge_objs, **case_obj})

    def result_converted(self, r_bool):
        if r_bool:
            return "Pass"
        else:
            return "Fail"


Application().main()
