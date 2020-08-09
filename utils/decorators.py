from functools import wraps
import jwt
from apps.users.models import User, Auth, AuthPermission
from .logger import logger


def authenticated_async(verify_is_admin=False):
    ''''
    JWT认证装饰器
    '''
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                Authorization = self.request.headers.get('Authorization', None)
                if not Authorization:
                    self.set_status(401)
                    return self.finish({"message": "身份认证信息未提供。", "errorCode": 2, "data": {}})
                auth_type, auth_token = Authorization.split(' ')
                data = jwt.decode(
                    auth_token,
                    self.settings['secret_key'],
                    leeway=self.settings['jwt_expire'],
                    options={"verify_exp": True}
                )
                user_id = data.get('id')
                user = await self.application.objects.get(
                    User,
                    id=user_id
                )
                if not user:
                    self.set_status(401)
                    return self.finish({"message": "用户不存在", "errorCode": 1, "data": {}})
                self._current_user = user
                await func(self, *args, **kwargs)
            except jwt.exceptions.ExpiredSignatureError as e:
                self.set_status(401)
                return self.finish({"message": "Token过期", "errorCode": 1, "data": {}})
            except jwt.exceptions.DecodeError as e:
                self.set_status(401)
                return self.finish({"message": "Token不合法", "errorCode": 1, "data": {}})
            except Exception as e:
                self.set_status(401)
                logger.error('出现异常：{}'.format(str(e)))
                return self.finish({"message": "Token异常", "errorCode": 2, "data": {}})
        return wrapper
    return decorator


def auth_validated(func):
    '''
    动态权限装饰器：根据用户的权限auth来判断对应的路由是否有权限：查看、新增、修改、删除
    '''
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        user = self._current_user
        if user.group.group_type != 'SuperAdmin':
            if not user.auth:
                return self.finish({"message": "非法用户，禁止访问。", "errorCode": 2, "data": {}})
            auth_name = '_'.join([item for item in self.request.path.split('/')[0:-1] if item != ''])
            query = AuthPermission.select().where(AuthPermission.auth_id == user.auth.id, AuthPermission.object_name == auth_name)
            auth_obj = await self.application.objects.execute(query)
            if not auth_obj:
                return self.finish({"message": "无权限，禁止访问。", "errorCode": 2, "data": {}})
            if self.request.method == 'GET' and not auth_obj[0].auth_list:
                return self.finish({"message": "无查看权限，禁止访问。", "errorCode": 2, "data": {}})
            if self.request.method == 'POST' and not auth_obj[0].auth_create:
                return self.finish({"message": "无新增权限，禁止访问。", "errorCode": 2, "data": {}})
            if self.request.method == 'PATCH' and not auth_obj[0].auth_update:
                return self.finish({"message": "无修改权限，禁止访问。", "errorCode": 2, "data": {}})
            if self.request.method == 'DELETE' and not auth_obj[0].auth_destroy:
                return self.finish({"message": "无删除权限，禁止访问。", "errorCode": 2, "data": {}})
        await func(self, *args, **kwargs)
    return wrapper


def validated_input_type(input_type = 'application/json'):
    '''
    验证输入参数的类型，例如只能输入json类型、formdata类型等。
    '''
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                if  self.request.headers.get("Content-Type") and self.request.headers.get("Content-Type").split(';')[0] != input_type:
                    return self.finish({"message": "只接受%s参数。" % input_type, "errorCode": 2, "data": {}})
                await func(self, *args, **kwargs)
            except Exception as e:
                self.set_status(200)
                logger.error('出现异常：{}'.format(str(e)))
                return self.finish({"message": str(e), "errorCode": 2, "data": {}})
        return wrapper
    return decorator