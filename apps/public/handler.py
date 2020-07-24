import json
import uuid
import os
import copy
from datetime import datetime, timedelta
import random
import logging
import aiofiles
import jwt
from playhouse.shortcuts import model_to_dict
import aioredis
from base.handler import BaseHandler
from utils.utils import create_code
from utils.decorators import authenticated_async, auth_validated, validated_input_type
from marshmallow import ValidationError
from base.settings import async_db, sync_db, FILE_CHECK, FILE_SIZE, SERVER_NAME
from .schemas import *
from .models import *
from celery_app.tasks import *
from celery.result import AsyncResult


class TestHandler(BaseHandler):
    '''
    测试接口
    get -> /public/test/
    '''
    async def get(self, *args, **kwargs):
        res_format = {"message": "ok", "errorCode": 0, "data": {}}
        try:
            res_format['message'] = 'Hello World'
            return self.finish(res_format)
        except Exception as e:
            print('出现异常：%s' % str(e))
            return self.finish({"message": "出现无法预料的异常：{}".format(str(e)), "errorCode": 1, "data": {}})


class UploadFileHandler(BaseHandler):
    '''
    上传文件接口
    post -> /public/uploadfile/
    '''
    @authenticated_async()
    @validated_input_type(input_type = 'multipart/form-data')
    async def post(self, *args, **kwargs):
        res_format = {"message": "ok", "errorCode": 0, "data": {}}
        try:
            # data = self.request.body.decode('utf-8') if self.request.body else "{}"
            # print(self.request.files.keys())
            # print(len(self.request.files.get('username')))
            # print(self.request.files.get('username')[0].keys())
            upload_host_url_list = []
            for key in self.request.files:
                # print(self.request.files.get(key)[0].keys())
                # print(len(self.request.files.get(key)[0]['body']) / 1024 / 1024)
                new_file_name = ''.join(str(uuid.uuid1()).split('-'))
                file_name = self.request.files.get(key)[0]['filename']
                file_size = len(self.request.files.get(key)[0]['body'])
                file_content = self.request.files.get(key)[0]['body']
                check_name = file_name.split('.')[-1]
                if check_name.lower() not in FILE_CHECK:
                    res_format['message'] = file_name + '不是规定的文件类型(%s)！' % '/'.join(FILE_CHECK)
                    res_format['errorCode'] = 2
                if file_size > FILE_SIZE:
                    res_format['message'] = file_name + '文件超过64mb，无法上传。'
                    res_format['errorCode'] = 2
                save_file_name = new_file_name + '.' + check_name
                upfile_base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static/files/')
                now_file_path = os.path.join(upfile_base_dir, str(datetime.now().date()))
                is_have = os.path.exists(now_file_path)
                if is_have:
                    save_path = os.path.join(now_file_path,save_file_name)
                else:
                    os.makedirs(now_file_path)
                    save_path = os.path.join(now_file_path, save_file_name)
                with open(save_path, 'wb') as u_file:
                    u_file.write(file_content)
                host_file_url = SERVER_NAME + '/files/' + save_file_name
                upload_host_url_list.append(host_file_url)
            res_format['data'] = upload_host_url_list if upload_host_url_list else {}
            return self.finish(res_format)
        except ValidationError as err:
            return self.finish({"message": str(err.messages), "errorCode": 2, "data": {}})
        except Exception as e:
            print('出现异常：%s' % str(e))
            return self.finish({"message": "出现无法预料的异常：{}".format(str(e)), "errorCode": 1, "data": {}})


class GetMobielCodeHandler(BaseHandler):
    '''
    获取手机验证码接口
    post -> /public/getcode/
    '''
    @validated_input_type()
    async def post(self, *args, **kwargs):
        res_format = {"message": "ok", "errorCode": 0, "data": {}}
        try:
            data = self.request.body.decode('utf-8') if self.request.body else "{}"
            validataed = GetMobielCoseSchema().load(json.loads(data))
            code = create_code(abc=False)
            # 异步创建验证码缓存
            # redis_pool = await aioredis.create_redis_pool('redis://127.0.0.1/0')
            redis_pool = await self.application.redis
            value = await redis_pool.get(validataed.get('mobile'), encoding='utf-8')
            if value:
                return self.finish({"message": "验证码已经发生，请勿重新发生", "errorCode": 2, "data": {}})
            await redis_pool.set(validataed.get('mobile'), code, expire=60 * 5)
            redis_pool.close()
            await redis_pool.wait_closed()
            return self.finish(res_format)
        except ValidationError as err:
            return self.finish({"message": str(err.messages), "errorCode": 2, "data": {}})
        except Exception as e:
            print('出现异常：%s' % str(e))
            return self.finish({"message": "出现无法预料的异常：{}".format(str(e)), "errorCode": 1, "data": {}})


class RunTaskHandler(BaseHandler):
    '''
    创建异步任务接口
    post -> /public/runtask/
    '''
    async def post(self, *args, **kwargs):
        res_format = {"message": "ok", "errorCode": 0, "data": {}}
        try:
            res = mul.delay(3,5)
            res_format['data']['task_id'] = res.id
            return self.finish(res_format)
        except Exception as e:
            print('出现异常：%s' % str(e))
            return self.finish({"message": "出现无法预料的异常：{}".format(str(e)), "errorCode": 1, "data": {}})


class GetTaskResultHandler(BaseHandler):
    '''
    获取异步任务结果
    get -> /public/getresult/
    '''
    async def get(self, *args, **kwargs):
        res_format = {"message": "ok", "errorCode": 0, "data": {}}
        try:
            task_id = self.get_query_argument('task_id', None)
            if not task_id:
                res_format['errorCode'] = 2
                res_format['message'] = '缺少任务唯一标识(get传参)：task_id'
                return self.finish(res_format)
            if AsyncResult(task_id).ready():
                res_format['data']['result'] = AsyncResult(task_id).result
            else:
                res_format['message'] = '任务进行中'
            return self.finish(res_format)
        except Exception as e:
            print('出现异常：%s' % str(e))
            return self.finish({"message": "出现无法预料的异常：{}".format(str(e)), "errorCode": 1, "data": {}})