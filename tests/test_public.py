import unittest
import os
from request_obj import BaseRequestObj


class TestSubtract(unittest.TestCase):

    def setUp(self):
        self.req_obj = BaseRequestObj()
        self.host_name = 'http://127.0.0.1:8080'

    def test_public_test(self):
        """
        未传参数
        :return:
        """
        res = self.req_obj.get_request(self.host_name + '/public/test/')
        status_code = res.status_code
        res_data = res.json()
        self.assertEqual(status_code, 200)
        self.assertEqual(res_data.get('errorCode'), 0)

    def test_public_test_params(self):
        """
        传入相关参数
        :return:
        """
        res = self.req_obj.get_request(self.host_name + '/public/test/', {'page': 1, 'page_size': 10})
        status_code = res.status_code
        res_data = res.json()
        self.assertEqual(status_code, 200)
        self.assertEqual(res_data.get('errorCode'), 0)


if __name__ == '__main__':
    '''
    verbosity默认为1
    0 (静默模式): 你只能获得总的测试用例数和总的结果。
    1 (默认模式): 非常类似静默模式 只是在每个成功的用例前面有个“.” 每个失败的用例前面有个 “E”
    2 (详细模式):测试结果会显示每个测试用例的所有相关的信息 并且 你在命令行里加入不同的参数可以起到一样的效果
    '''
    unittest.main(verbosity=2)
