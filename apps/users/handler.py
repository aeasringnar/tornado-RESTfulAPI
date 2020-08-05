import json
import uuid
import os
from datetime import datetime, timedelta
import time
import random
import logging
import aiofiles
import jwt
from playhouse.shortcuts import model_to_dict
from base.handler import BaseHandler
from apps.users.models import Group, Auth, AuthPermission, User
from utils import utils
from utils.decorators import authenticated_async, auth_validated, validated_input_type
from .schemas import AuthSerializer, AuthPermissionSerializer, NewUserSerializer, AddUserSchema, ReturnUserSchema, UpdateUserSchema, MobielLoginSchema, AdminLoginSchema, AddAuthSchema, UpdateAuthSchema, \
    ChangeUserSchema
from marshmallow import ValidationError
from base.settings import async_db, sync_db
from utils.logger import logger
import copy
from tornado.websocket import WebSocketHandler
from utils.caches import cache_data


class MobileLoginHandler(BaseHandler):
    '''
    手机号登录
    POST -> /mobilelogin/
    payload:
        {
            "mobile": "手机号",
            "code": "验证码"
        }
    '''
    @validated_input_type()
    async def post(self, *args, **kwargs):
        res_format = {"message": "ok", "errorCode": 0, "data": {}}
        try:
            data = self.request.body.decode('utf-8') if self.request.body else "{}"
            validataed = MobielLoginSchema().load(json.loads(data))
            mobile = validataed['mobile']
            code = validataed['code']
            redis_pool = await aioredis.create_redis_pool('redis://127.0.0.1/0')
            value = await redis_pool.get(mobile, encoding='utf-8')
            if not value:
                return self.finish({"message": "验证码不存在，请重新发生验证码。", "errorCode": 2, "data": {}})
            if value != code:
                return self.finish({"message": "验证码错误，请核对后重试。", "errorCode": 2, "data": {}})
            redis_pool.close()
            await redis_pool.wait_closed()
            query = User.select().where(User.mobile == mobile)
            user = await self.application.objects.execute(query)
            if not user:
                # 创建用户
                user = await self.application.objects.create(
                    User,
                    username = mobile,
                    mobile = mobile,
                    group_id = 3
                )
            else:
                user = user[0]
            payload = {
                'id': user.id,
                'username': user.username,
                'exp': datetime.utcnow()
            }
            token = jwt.encode(payload, self.settings["secret_key"], algorithm='HS256')
            res_format['data']['token'] = token.decode('utf-8')
            return self.finish(res_format)
        except ValidationError as err:
            return self.finish({"message": str(err.messages), "errorCode": 2, "data": {}})
        except Exception as e:
            logger.error('出现异常：%s' % str(e))
            return self.finish({"message": "出现无法预料的异常：{}".format(str(e)), "errorCode": 1, "data": {}})


'''
    res_format = {"message": "ok", "errorCode": 0, "data": {}}
        try:
            data = self.request.body.decode('utf-8') if self.request.body else "{}"
            if not json.loads(data):
                return self.finish(res_format)
            validataed = BaseSchema().load(json.loads(data))
            return self.finish(res_format)
        except ValidationError as err:
            return self.finish({"message": str(err.messages), "errorCode": 2, "data": {}})
        except Exception as e:
            print('出现异常：%s' % str(e))
            return self.finish({"message": "出现无法预料的异常：{}".format(str(e)), "errorCode": 1, "data": {}})
'''


class AdminLoginHandler(BaseHandler):
    '''
    用户登录
    POST -> /login/
    payload:
        {
            "username": "用户名或者邮箱",
            "password": "密码"
        }
    '''
    @validated_input_type()
    async def post(self, *args, **kwargs):
        res_format = {"message": "ok", "errorCode": 0, "data": {}}
        try:
            data = self.request.body.decode('utf-8') if self.request.body else "{}"
            validataed = AdminLoginSchema().load(json.loads(data))
            username = validataed['username']
            password = validataed['password']
            query = User.select().where((User.username==username) | (User.email==username) | ((User.mobile==username)))
            user = await self.application.objects.execute(query)
            if not user:
                res_format['message'] = '用户不存在'
                res_format['errorCode'] = 2
                return self.finish(res_format)
            user = user[0]
            if not user.password.check_password(password):
                res_format['message'] = '密码错误'
                res_format['errorCode'] = 2
                return self.finish(res_format)
            payload = {
                'id': user.id,
                'username': username,
                'exp': datetime.utcnow()
            }
            token = jwt.encode(payload, self.settings["secret_key"], algorithm='HS256')
            res_format['data']['token'] = token.decode('utf-8')
            return self.finish(res_format)
        except ValidationError as err:
            return self.finish({"message": str(err.messages), "errorCode": 2, "data": {}})
        except Exception as e:
            logger.error('出现异常：%s' % str(e))
            return self.finish({"message": "出现无法预料的异常：{}".format(str(e)), "errorCode": 1, "data": {}})


class UserInfoHandler(BaseHandler):
    '''
    读取用户资料
    get -> /userinfo/

    部分更新用户资料
    patch -> /userinfo/
    payload:
        {
            "username": "用户名",
            "gender": "性别",
            "nick_name": "昵称",
            "region": "地址",
            "avatar_url": "头像",
            "birth_date": "生日"
        }

    '''
    @authenticated_async()
    @validated_input_type()
    async def get(self, *args, **kwargs):
        res_format = {"message": "ok", "errorCode": 0, "data": {}}
        try:
            user = self.current_user
            res_format['data'] = json.loads(ReturnUserSchema().dumps(user))
            return self.finish(res_format)
        except Exception as e:
            logger.error('出现异常：%s' % str(e))
            return self.finish({"message": "出现无法预料的异常：{}".format(str(e)), "errorCode": 1, "data": {}})

    @authenticated_async()
    @validated_input_type()
    async def patch(self, *args, **kwargs):
        user = self.current_user
        res_format = {"message": "ok", "errorCode": 0, "data": {}}
        try:
            data = self.request.body.decode('utf-8') if self.request.body else "{}"
            if not json.loads(data):
                return self.finish(res_format)
            validataed = ChangeUserSchema().load(json.loads(data))
            query = User.select(User.id, User.username, User.mobile).where(
                User.username == validataed.get('username')
            ).where(
                User.id != user.id
            )
            # print(query)
            check_unique = await self.application.objects.execute(query)
            if check_unique:
                res_format['message'] = '用户名已存在'
                res_format['errorCode'] = 2
                return self.finish(res_format)
            [setattr(user, key, val) for key,val in validataed.items()]
            await self.application.objects.update(user)
            res_format['data'] = json.loads(ChangeUserSchema().dumps(user))
            return self.finish(res_format)
        except ValidationError as err:
            return self.finish({"message": str(err.messages), "errorCode": 2, "data": {}})
        except Exception as e:
            logger.error('出现异常：%s' % str(e))
            return self.finish({"message": "出现无法预料的异常：{}".format(str(e)), "errorCode": 1, "data": {}})


class AuthHandler(BaseHandler):
    '''
    获取权限列表
    get -> /adminauth/
    检索权限
    get -> /adminauth/<pk>
    新增权限
    post -> /adminauth/
    修改权限
    patch -> /adminauth/<pk>
    删除权限
    delete -> /adminauth/<pk>
    base payload:
        {
            "auth_type": "测试权限",
            "auth_permissions": [
                {
                    "object_name":"user",
                    "object_name_cn":"用户管理",
                    "auth_list":1,
                    "auth_create":1,
                    "auth_update":1,
                    "auth_destroy":1,
                }
            ]
        }
    '''
    @authenticated_async()
    @auth_validated
    @validated_input_type()
    async def get(self, *args, **kwargs):
        res_format = {"message": "ok", "errorCode": 0, "data": {}}
        search_ls = ['auth_type']
        filter_ls = ['auth_type']
        try:
            data = self.request.body.decode('utf-8') if self.request.body else "{}"
            page = eval(self.get_query_argument(self.settings['default_page_param'], '1'))
            page_size = eval(self.get_query_argument('page_size', self.settings['default_page_size']))
            search_str = self.get_query_argument('search', '')
            pk = kwargs.get('pk')
            if pk:
                query = Auth.select().where(Auth.id==int(pk))
                auth = await self.application.objects.execute(query)
                if len(auth) > 0:
                    query = AuthPermission.select().where(AuthPermission.auth_id == auth[0].id)
                    auth_permissions = await self.application.objects.execute(query)
                    auth_obj = json.loads(AuthSerializer().dumps(auth[0]))
                    auth_obj['auth_permissions'] = json.loads(AuthPermissionSerializer(many=True).dumps(auth_permissions))
                    res_format['data'] = auth_obj
            else:
                query = Auth.select().where(Auth.auth_type.contains(search_str)).order_by(-Auth.id).paginate(page=page, paginate_by=page_size)
                # print('查看SQL：', query)
                auths = await self.application.objects.execute(query)
                total = await self.application.objects.count(Auth.select())
                # total = await self.application.objects.count(Auth.select(Auth.id).where(Auth.id > 0))
                auth_ids = [item.id for item in auths]
                query = AuthPermission.select().where(AuthPermission.auth_id in auth_ids)
                # print('查看SQL：', query)
                all_auth_permission = await self.application.objects.execute(query)
                permission_dics = json.loads(AuthPermissionSerializer(many=True).dumps(all_auth_permission))
                auth_dics = json.loads(AuthSerializer(many=True).dumps(auths))
                for item in auth_dics:
                    item['auth_permissions'] = list(filter(lambda x : x.get('auth_id') == item.get('id'),permission_dics))
                res_format['total'] = total
                res_format['data'] = auth_dics
            return self.finish(res_format)
        except Exception as e:
            logger.error('出现异常：%s' % str(e))
            return self.finish({"message": "出现无法预料的异常：{}".format(str(e)), "errorCode": 1, "data": {}})

    @authenticated_async()
    @auth_validated
    @validated_input_type()
    async def patch(self, *args, **kwargs):
        res_format = {"message": "ok", "errorCode": 0, "data": {}}
        try:
            data = self.request.body.decode('utf-8') if self.request.body else "{}"
            if not json.loads(data):
                return self.finish(res_format)
            pk = kwargs.get('pk')
            if not pk:
                res_format['message'] = '路由异常，请携带id'
                res_format['errorCode'] = 2
                return self.finish(res_format)
            validataed = AddAuthSchema().load(json.loads(data))
            auth_type = validataed['auth_type']
            query = Auth.select().where(Auth.id == int(pk))
            check_obj = await self.application.objects.execute(query)
            if not check_obj:
                res_format['message'] = '资源不存在'
                res_format['errorCode'] = 2
                return self.finish(res_format)
            auth_type = validataed['auth_type']
            query = Auth.select().where(
                Auth.auth_type == auth_type,
                Auth.id != int(pk)
            )
            check_unique = await self.application.objects.execute(query)
            if check_unique:
                res_format['message'] = '权限名称已存在'
                res_format['errorCode'] = 2
                return self.finish(res_format)
            # check_obj[0].auth_type = auth_type
            setattr(check_obj[0], 'auth_type', auth_type)
            await self.application.objects.update(check_obj[0])
            with sync_db.atomic():
                AuthPermission.delete().where(AuthPermission.auth_id == int(pk)).execute()
                for item in validataed['auth_permissions']:
                    item['auth_id'] = int(pk)
                AuthPermission.insert_many(validataed['auth_permissions']).execute()
            return self.finish(res_format)
        except ValidationError as err:
            return self.finish({"message": str(err.messages), "errorCode": 2, "data": {}})
        except Exception as e:
            logger.error('出现异常：%s' % str(e))
            return self.finish({"message": "出现无法预料的异常：{}".format(str(e)), "errorCode": 1, "data": {}})

    @authenticated_async()
    @auth_validated
    @validated_input_type()
    async def post(self, *args, **kwargs):
        res_format = {"message": "ok", "errorCode": 0, "data": {}}
        try:
            data = self.request.body.decode('utf-8') if self.request.body else "{}"
            pk = kwargs.get('pk')
            if pk:
                res_format['message'] = '不支持的方法，请检查路由是否正确。'
                res_format['errorCode'] = 2
                return self.finish(res_format)
            validataed = AddAuthSchema().load(json.loads(data))
            auth_type = validataed['auth_type']
            query = Auth.select(Auth.id, Auth.auth_type).where(Auth.auth_type==auth_type) # 数据增大后明显耗时
            auth = await self.application.objects.execute(query)
            if auth:
                res_format['message'] = '该权限已存在'
                res_format['errorCode'] = 2
                return self.finish(res_format)
            async with async_db.atomic_async() as transaction:
                # 创建权限
                auth = await self.application.objects.create(
                    Auth,
                    auth_type = auth_type
                )
                # 批量创建权限功能
                for item in validataed['auth_permissions']:
                    item['auth_id'] = auth.id
                    await self.application.objects.create(
                        AuthPermission,
                        **item
                    )
            return self.finish(res_format)
        except ValidationError as err:
            return self.finish({"message": str(err.messages), "errorCode": 2, "data": {}})
        except Exception as e:
            logger.error('出现异常：%s' % str(e))
            return self.finish({"message": "出现无法预料的异常：{}".format(str(e)), "errorCode": 1, "data": {}})

    @authenticated_async()
    @auth_validated
    @validated_input_type()
    async def delete(self, *args, **kwargs):
        res_format = {"message": "ok", "errorCode": 0, "data": {}}
        try:
            data = self.request.body.decode('utf-8') if self.request.body else "{}"
            pk = kwargs.get('pk')
            if not pk:
                res_format['message'] = '路由异常，请携带id'
                res_format['errorCode'] = 2
                return self.finish(res_format)
            query = Auth.select().where(Auth.id == int(pk))
            check_obj = await self.application.objects.execute(query)
            if not check_obj:
                res_format['message'] = '资源不存在'
                res_format['errorCode'] = 2
                return self.finish(res_format)
            await self.application.objects.delete(check_obj[0])
            return self.finish(res_format)
        except Exception as e:
            logger.error('出现异常：%s' % str(e))
            return self.finish({"message": "出现无法预料的异常：{}".format(str(e)), "errorCode": 1, "data": {}})


class AdminUserHandler(BaseHandler):
    '''
    获取员工列表
    get -> /adminuser/
    检索员工
    get -> /adminuser/<pk>
    新增员工
    post -> /adminuser/
    修改员工
    patch -> /adminuser/<pk>
    删除员工
    delete -> /adminuser/<pk>
    base payload:
        {
            "username": "用户名",
            "password": "密码",
            "mobile": "手机号或电话",
            "email": "邮箱",
            "real_name": "真实姓名",
            "nick_name": "昵称",
            "region": "区域",
            "avatar_url": "头像地址",
            "gender": "性别",
            "birth_date": "生日",
            "group_id": "用户组id",
            "auth_id": "权限id"
        }
    '''
    @authenticated_async()
    @auth_validated
    @validated_input_type()
    @cache_data()
    async def get(self, *args, **kwargs):
        res_format = {"message": "ok", "errorCode": 0, "data": {}}
        search_ls = ['auth_type']
        filter_ls = ['auth_type']
        try:
            data = self.request.body.decode('utf-8') if self.request.body else "{}"
            page = eval(self.get_query_argument(self.settings['default_page_param'], '1'))
            page_size = eval(self.get_query_argument('page_size', self.settings['default_page_size']))
            search_str = self.get_query_argument('search', '')
            pk = kwargs.get('pk')
            if pk:
                query = User.select().where(User.id==int(pk))
                auth = await self.application.objects.execute(query)
                if len(auth) > 0:
                    res_format['data'] = json.loads(ReturnUserSchema().dumps(auth[0]))
            else:
                query = User.select().order_by(-User.id).paginate(page=page, paginate_by=page_size)
                objs = await self.application.objects.execute(query)
                total = await self.application.objects.count(User.select())
                res_format['total'] = total
                res_format['data'] = json.loads(ReturnUserSchema(many=True).dumps(objs))
            self.finish(res_format)
            return res_format
        except Exception as e:
            logger.error('出现异常：%s' % str(e))
            return self.finish({"message": "出现无法预料的异常：{}".format(str(e)), "errorCode": 1, "data": {}})

    @authenticated_async()
    @auth_validated
    @validated_input_type()
    async def patch(self, *args, **kwargs):
        res_format = {"message": "ok", "errorCode": 0, "data": {}}
        try:
            data = self.request.body.decode('utf-8') if self.request.body else "{}"
            if not json.loads(data):
                return self.finish(res_format)
            pk = kwargs.get('pk')
            if not pk:
                res_format['message'] = '路由异常，请携带id'
                res_format['errorCode'] = 2
                return self.finish(res_format)
            validataed = UpdateUserSchema().load(json.loads(data))
            # print(validataed, type(validataed))
            query = Auth.select().where(Auth.id == int(pk))
            check_obj = await self.application.objects.execute(query)
            if not check_obj:
                res_format['message'] = '资源不存在'
                res_format['errorCode'] = 2
                return self.finish(res_format)
            query = User.select(User.id, User.username, User.mobile).where(
                (User.username == validataed.get('username')) | (User.mobile == validataed.get('mobile'))
            ).where(
                User.id != int(pk)
            )
            # print(query)
            check_unique = await self.application.objects.execute(query)
            if check_unique:
                res_format['message'] = '用户名或手机号已存在'
                res_format['errorCode'] = 2
                return self.finish(res_format)
            [setattr(check_obj[0], key, val) for key,val in validataed.items()]
            await self.application.objects.update(check_obj[0])
            return self.finish(res_format)
        except ValidationError as err:
            return self.finish({"message": str(err.messages), "errorCode": 2, "data": {}})
        except Exception as e:
            logger.error('出现异常：%s' % str(e))
            return self.finish({"message": "出现无法预料的异常：{}".format(str(e)), "errorCode": 1, "data": {}})

    @authenticated_async()
    @auth_validated
    @validated_input_type()
    async def post(self, *args, **kwargs):
        res_format = {"message": "ok", "errorCode": 0, "data": {}}
        try:
            # print()
            data = self.request.body.decode('utf-8') if self.request.body else "{}"
            # print(data)
            # un_validata = NewUserSerializer.from_json(json.loads(data))
            pk = kwargs.get('pk')
            if pk:
                res_format['message'] = '不支持的方法，请检查路由是否正确。'
                res_format['errorCode'] = 2
                return self.finish(res_format)
            validataed = AddUserSchema().load(json.loads(data))
            # print(validataed, type(validataed))
            username = validataed.get('username')
            query = User.select().where(User.username==username)
            checks = await self.application.objects.execute(query)
            if checks:
                res_format['message'] = '该用户名已存在'
                res_format['errorCode'] = 2
                return self.finish(res_format)
            await self.application.objects.create(User, **validataed)
            return self.finish(res_format)
        except ValidationError as err:
            return self.finish({"message": str(err.messages), "errorCode": 2, "data": {}})
        except Exception as e:
            logger.error('出现异常：%s' % str(e))
            return self.finish({"message": "出现无法预料的异常：{}".format(str(e)), "errorCode": 1, "data": {}})

    @authenticated_async()
    @auth_validated
    @validated_input_type()
    async def delete(self, *args, **kwargs):
        res_format = {"message": "ok", "errorCode": 0, "data": {}}
        try:
            data = self.request.body.decode('utf-8') if self.request.body else "{}"
            pk = kwargs.get('pk')
            if not pk:
                res_format['message'] = '路由异常，请携带id'
                res_format['errorCode'] = 2
                return self.finish(res_format)
            query = User.select().where(User.id == int(pk))
            check_obj = await self.application.objects.execute(query)
            if not check_obj:
                res_format['message'] = '资源不存在'
                res_format['errorCode'] = 2
                return self.finish(res_format)
            await self.application.objects.delete(check_obj[0])
            return self.finish(res_format)
        except Exception as e:
            logger.error('出现异常：%s' % str(e))
            return self.finish({"message": "出现无法预料的异常：{}".format(str(e)), "errorCode": 1, "data": {}})



# 测试开发WebSocket
class EchoWebSocket(WebSocketHandler):
    def open(self):
        print("发现新的连接")
        print(self)

    def on_message(self, message):
        print('收到消息：%s，类型：%s' % (message, str(type(message))))
        self.write_message(u"You said: " + message)

    def on_close(self):
        print("发现有连接关闭")
        print(self)

    def check_origin(self, origin):
        # 允许WebSocket的跨域请求
        return True