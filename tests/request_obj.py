import requests
import os
import json
import random
from io import BytesIO
from requests_toolbelt import MultipartEncoder
'''
注意：本程序诊断RESTfulAPI接口的测试，返回数据均为json格式。
使用 requests 请求返回的 response 注意事项
response.text 获得响应结果的字符串类型
response.content 获得响应结果的bytes(二进制数据流类型，可用来处理返回的二进制文件流) 如果是图片的话可以使用 Image.open(BytesIO(r.content)).show() 打开查看
response.status_code 获得响应结果的状态码
response.headers 获得响应结果的请求头
response.encoding 获得响应结果的编码
response.url 获得请求的url
response.json() 将获得响应结果转换成 json.loads(str) 后的结果，在python中得到字典类型
'''

class BaseRequestObj(object):
    '''
    请求基类
    '''
    angents = [
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
        "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    ]
    def __init__(self):
        self.request = requests
        self.default_headers = {'User-Agent': random.choice(self.angents)}

    def get_request(self, url, params=None, headers=None):
        '''
        发起GET请求
        :url 请求的地址 字符串类型
        :params GET请求参数 字典类型
        :headers 定义请求头 字典类型
        '''
        # default_headers = {'Content-Type': 'multipart/form-data'}
        if headers:
            self.default_headers.update(headers)
        return self.request.get(url=url, params=params, headers=self.default_headers)
    
    def post_json_request(self, url, data, headers=None):
        '''
        发起POST请求 发送json请求体
        :url 请求的地址 字符串类型
        :data json类型请求体 字典类型
        :headers 定义请求头 字典类型
        '''
        self.default_headers.update({'Content-Type': 'application/json'})
        if headers:
            self.default_headers.update(headers)
        return self.request.post(url=url, data=json.dumps(data), headers=self.default_headers)

    def patch_json_request(self, url, data, headers=None):
        '''
        发起PATCH请求 发送json请求体
        :url 请求的地址 字符串类型
        :data json类型请求体 字典类型
        :headers 定义请求头 字典类型
        '''
        self.default_headers.update({'Content-Type': 'application/json'})
        if headers:
            self.default_headers.update(headers)
        return self.request.patch(url=url, data=json.dumps(data), headers=self.default_headers)
    
    def put_json_request(self, url, data, headers=None):
        '''
        发起PUT请求 发送json请求体
        :url 请求的地址 字符串类型
        :data json类型请求体 字典类型
        :headers 定义请求头 字典类型
        '''
        self.default_headers.update({'Content-Type': 'application/json'})
        if headers:
            self.default_headers.update(headers)
        return self.request.put(url=url, data=json.dumps(data), headers=self.default_headers)
    
    def delete_request(self, url, headers=None):
        '''
        发起DELETE请求
        :url 请求的地址 字符串类型
        '''
        self.default_headers.update({'Content-Type': 'application/json'})
        if headers:
            self.default_headers.update(headers)
        return self.request.delete(url=url, headers=self.default_headers)
    
    def post_files_request(self, url, files, headers=None):
        '''
        发起POST请求 请求体为文件
        :url 请求的地址 字符串类型
        :files 文件类型请求体 文件类型 例：{'file1': open('img1.png', 'rb'), 'file2': open('1.xls', 'rb')}
        :headers 定义请求头 字典类型
        '''
        if headers:
            self.default_headers.update(headers)
        return self.request.post(url=url, files=files, headers=self.default_headers)


if __name__ == '__main__':
    req_obj = BaseRequestObj()
    # print(req_obj.get_request('http://127.0.0.1:8080/public/test/', {'page': 1, 'page_size': 2}).json())
    # print(req_obj.post_json_request('http://127.0.0.1:8080/public/test/', {'page': 1, 'page_size': 2}).json())
    # print(req_obj.patch_json_request('http://127.0.0.1:8080/public/test/', {'page': 1, 'page_size': 2}).json())
    # print(req_obj.put_json_request('http://127.0.0.1:8080/public/test/', {'page': 1, 'page_size': 2}).json())
    # file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.py')
    # print(req_obj.post_files_request('http://127.0.0.1:8080/public/uploadfile/', {'file': open(file_path, 'rb')}).json())
