from marshmallow import Schema, fields, ValidationError, validate, validates, pre_load, validates_schema
from base.schema import BaseSchema


class UserSerializer(BaseSchema):
    id = fields.Int(dump_only=True)
    username = fields.String()
    email = fields.Email()
    gender = fields.String()


class AuthPermissionSerializer(BaseSchema):
    id = fields.Int(dump_only=True)
    object_name = fields.String()
    object_name_cn = fields.String()
    auth_id = fields.Int()
    auth_list = fields.Int()
    auth_create = fields.Int()
    auth_update = fields.Int()
    auth_destroy = fields.Int()


class AuthSerializer(BaseSchema):
    id = fields.Int(dump_only=True)
    auth_type = fields.String()


def validate_name(data):
    if not data:
        raise ValidationError("username字段不能为空字符串")
    if len(data) <= 2:
        raise ValidationError("username长度必须大于2位")
    if len(data) >= 6:
        raise ValidationError("username长度不能大于6位")

class NewUserSerializer(BaseSchema):
    '''
    1、必须要传的字段，但是可以为空字符串 required=True
    2、必须要传的字段，并且不能为空字符串 required=True 、配合validate验证非空字符串
    3、非必传字段，但是一旦传了就不能传空字符串，直接使用validate验证非空字符串即可
    4、validate可以使用官方的验证器：Email、Equal、Length、Range等等
    '''
    id = fields.Int(dump_only=True)
    username = fields.String(required=True, validate=validate_name, error_messages={"required": "username字段必须填写"}) # 即不允许不传username字段，并且不允许username字段为空字符串
    username = fields.String(validate=validate_name)
    mobile = fields.String(required=True, error_messages={"required": "mobile字段必须填写"}) # 运行mobile传入空字符串，但是不允许不传mobile字段
    email = fields.String(validate=validate.Email(error='输入的邮箱格式不正确。'))
    # email = fields.String(validate=[validate.Email()])
    # email = fields.String()
    real_name = fields.String()
    nick_name = fields.String(validate=validate.Length(min=5,max=32, error='昵称长度必须在5到32个字符。'))
    region = fields.String()
    avatar_url = fields.String()
    gender = fields.String()
    birth_date = fields.Date("%Y-%m-%d")
    # group = fields.String()
    # auth = fields.String()
    bf_logo_time = fields.DateTime("%Y-%m-%d %H:%M:%S")

    # 在内部使用装饰器的方式验证real_name字段，实现效果和username内的validate是一致的。实际中建议使用装饰器的方法实现。
    @validates('real_name')
    def validate_real_name(self, data):
        if not data:
            raise ValidationError("real_name字段不能为空字符串")
        if len(data) <= 5:
            raise ValidationError("real_name长度必须大于5位")
        if len(data) >= 32:
            raise ValidationError("real_name长度不能大于32位")

    '''
    常用的装饰器
    post_dump（[fn，pass_many，pass_original]）注册要在序列化对象后调用的方法，它会在对象序列化后被调用。
    post_load（[fn，pass_many，pass_original]）注册反序列化对象后要调用的方法，它会在验证数据之后被调用。
    pre_dump（[fn，pass_many]）注册要在序列化对象之前调用的方法，它会在序列化对象之前被调用。
    pre_load（[fn，pass_many]）在反序列化对象之前，注册要调用的方法，它会在验证数据之前调用。
    validates（field_name）注册一个字段验证器，对指定字段设置验证器。
    '''


class MobielLoginSchema(BaseSchema):
    mobile = fields.String(label='手机号', required=True, error_messages={"required": "请输入手机号。"})
    code = fields.String(label='验证码', required=True, error_messages={"required": "请输入验证码。"})


class AdminLoginSchema(BaseSchema):
    username = fields.String(label='用户名', required=True, error_messages={"required": "请输入用户名。"})
    password = fields.String(label='密码', required=True, error_messages={"required": "请输入密码。"})


class AddUserSchema(BaseSchema):
    username = fields.String(label='用户名', required=True, validate=validate.Length(min=3,max=32, error='用户名长度必须在3到32个字符。'), error_messages={"required": "用户名为必传项。"})
    password = fields.String(label='密码', required=True, validate=validate.Length(min=3,max=32, error='密码长度必须在3到32个字符。'), error_messages={"required": "密码为必传项。"})
    mobile = fields.String(label='手机号或电话', required=True, error_messages={"required": "手机号或电话为必传项。"})
    email = fields.String(label='邮箱', validate=validate.Email(error='输入的邮箱格式不正确。'))
    real_name = fields.String(label='真实姓名', validate=validate.Length(min=1,max=32, error='真实姓名长度必须在1到32个字符。'))
    nick_name = fields.String(label='昵称', validate=validate.Length(min=3,max=32, error='昵称长度必须在3到32个字符。'))
    region = fields.String(label='区域')
    avatar_url = fields.String(label='头像地址')
    gender = fields.Integer(label='性别')
    birth_date = fields.Date(label='出生日期', format="%Y-%m-%d")
    group_id = fields.Integer(label='用户组', required=True, error_messages={"required": "用户组为必传项。"})
    auth_id = fields.Integer(label='权限', error_messages={'invalid': '权限id必须为整数类型'})

    @validates('mobile')
    def validate_mobile(self, data):
        if len(data) not in [11, 12]:
            raise ValidationError("手机号或电话格式不正确。")
    
    @validates('auth_id') # 时间上这里验证都是延后与字段本身属性的验证，例如auth_id会对传入的数据进行数字验证，该验证早于validates
    def validate_auth(self, data):
        if not data:
            raise ValidationError("权限id不允许为空字符串。")
        if not isinstance(data, int):
            raise ValidationError("权限id必须为整数。")

    @pre_load
    def process_input(self, data, **kwargs):
        '''设置在验证数据之后将邮箱字段的值全部转小写，并去除前后空格。'''
        if data.get('email'):
            data['email'] = data.get('email').lower().strip()
        # if data.get('auth_id') and not isinstance(data.get('auth_id'), int): # 这里 可以做部分验证，实在找不到好的验证方法时
        #     raise ValidationError("权限id必须为整数。")
        return data


class ChangeUserSchema(BaseSchema):
    username = fields.String(label='用户名', validate=validate.Length(min=3,max=32, error='昵称长度必须在3到32个字符。'))
    nick_name = fields.String(label='昵称', validate=validate.Length(min=3,max=32, error='昵称长度必须在3到32个字符。'))
    region = fields.String(label='区域')
    avatar_url = fields.String(label='头像地址')
    gender = fields.Integer(label='性别')
    birth_date = fields.Date(label='出生日期', format="%Y-%m-%d")


class UpdateUserSchema(BaseSchema):
    username = fields.String(label='用户名')
    password = fields.String(label='密码')
    mobile = fields.String(label='手机号或电话')
    email = fields.String(label='邮箱', validate=validate.Email(error='输入的邮箱格式不正确。'))
    real_name = fields.String(label='真实姓名', validate=validate.Length(min=1,max=32, error='真实姓名长度必须在1到32个字符。'))
    nick_name = fields.String(label='昵称', validate=validate.Length(min=3,max=32, error='昵称长度必须在3到32个字符。'))
    region = fields.String(label='区域')
    avatar_url = fields.String(label='头像地址')
    gender = fields.Integer(label='性别')
    birth_date = fields.Date(label='出生日期', format="%Y-%m-%d")
    group_id = fields.Integer(label='用户组', error_messages={'invalid': '用户组id必须为整数类型'})
    auth_id = fields.Integer(label='权限', error_messages={'invalid': '权限id必须为整数类型'})

    @validates('mobile')
    def validate_mobile(self, data):
        if len(data) not in [11, 12]:
            raise ValidationError("手机号或电话格式不正确。")

    @pre_load
    def process_input(self, data, **kwargs):
        '''设置在验证数据之后将邮箱字段的值全部转小写，并去除前后空格。'''
        if data.get('email'):
            data['email'] = data.get('email').lower().strip()
        return data


class UserUseGroupSchema(BaseSchema):
    group_type = fields.String()
    group_type_cn = fields.String()


class ReturnUserSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    username = fields.String(label='用户名', dump_only=True)
    # password = fields.String(label='密码', dump_only=True)
    mobile = fields.String(label='手机号或电话', dump_only=True)
    email = fields.String(label='邮箱', dump_only=True)
    real_name = fields.String(label='真实姓名', dump_only=True)
    nick_name = fields.String(label='昵称', dump_only=True)
    region = fields.String(label='区域', dump_only=True)
    # avatar_url = fields.String(label='头像地址', dump_only=True)
    avatar_url = fields.String(label='头像地址', dump_only=True)
    gender = fields.Integer(label='性别', dump_only=True)
    birth_date = fields.Date(label='出生日期', format="%Y-%m-%d", dump_only=True)
    # group_id = fields.Integer(label='用户组', dump_only=True)
    group = fields.Nested(UserUseGroupSchema(exclude=("update_time", "create_time")), dump_only=True)
    auth_id = fields.Integer(label='权限', dump_only=True)


class AddAuthPermissionSchema(BaseSchema):
    object_name = fields.String(label= "功能名称", required=True, error_messages={"required": "功能名称为必传项。"})
    object_name_cn = fields.String(label= "功能名称-cn", required=True, error_messages={"required": "功能名称-cn为必传项。"})
    auth_list = fields.Integer(label= "查看", choices= ((0,'否'),(1,'是')), required=True, error_messages={'required': '查看功能为必传项。', 'invalid': '查看功能必须为整数类型'})
    auth_create = fields.Integer(label= "创建", choices= ((0,'否'),(1,'是')), required=True, error_messages={'required': '创建功能为必传项。', 'invalid': '创建功能必须为整数类型'})
    auth_update = fields.Integer(label= "修改", choices= ((0,'否'),(1,'是')), required=True, error_messages={'required': '修改功能为必传项。', 'invalid': '修改功能必须为整数类型'})
    auth_destroy = fields.Integer(label= "删除", choices= ((0,'否'),(1,'是')), required=True, error_messages={'required': '删除功能为必传项。', 'invalid': '删除功能必须为整数类型'})

    class Meta:
        strict = True # 定义strict=True，则一次可对多个字段进行验证

    @validates_schema
    def validate_func(self, data, **kwargs):
        if data['auth_create'] not in [0, 1, '0', '1']:
            raise ValidationError("值必须为0或1")
        if data['auth_destroy'] not in [0, 1, '0', '1']:
            raise ValidationError("值必须为0或1")
        if data['auth_list'] not in [0, 1, '0', '1']:
            raise ValidationError("值必须为0或1")
        if data['auth_update'] not in [0, 1, '0', '1']:
            raise ValidationError("值必须为0或1")


class AddAuthSchema(BaseSchema):
    auth_type = fields.String(label= "权限名称", required=True, error_messages={"required": "权限名称为必传项。"})
    auth_permissions = fields.List(fields.Nested(AddAuthPermissionSchema()), required=True, error_messages={"required": "至少输入一个功能权限明细。"})


class UpdateAuthSchema(BaseSchema):
    auth_type = fields.String(label= "权限名称")
    auth_permissions = fields.List(fields.Nested(AddAuthPermissionSchema()), required=True, error_messages={"required": "至少输入一个功能权限明细。"})


############################ crud use schema
from utils.crudSchema import CrudBaseSchema


class CrudUseAddUserSchema(CrudBaseSchema):
    username = fields.String(label='用户名', required=True, validate=validate.Length(min=3,max=32, error='用户名长度必须在3到32个字符。'), error_messages={"required": "用户名为必传项。"})
    password = fields.String(label='密码', required=True, validate=validate.Length(min=3,max=32, error='密码长度必须在3到32个字符。'), error_messages={"required": "密码为必传项。"})
    mobile = fields.String(label='手机号或电话', required=True, error_messages={"required": "手机号或电话为必传项。"})
    email = fields.String(label='邮箱', validate=validate.Email(error='输入的邮箱格式不正确。'))
    real_name = fields.String(label='真实姓名', validate=validate.Length(min=1,max=32, error='真实姓名长度必须在1到32个字符。'))
    nick_name = fields.String(label='昵称', validate=validate.Length(min=3,max=32, error='昵称长度必须在3到32个字符。'))
    region = fields.String(label='区域')
    avatar_url = fields.String(label='头像地址')
    gender = fields.Integer(label='性别')
    birth_date = fields.Date(label='出生日期', format="%Y-%m-%d")
    group_id = fields.Integer(label='用户组', required=True, error_messages={"required": "用户组为必传项。"})
    auth_id = fields.Integer(label='权限', error_messages={'invalid': '权限id必须为整数类型'})

    @validates('mobile')
    def validate_mobile(self, data):
        if len(data) not in [11, 12]:
            raise ValidationError("手机号或电话格式不正确。")
    
    @validates('auth_id') # 时间上这里验证都是延后与字段本身属性的验证，例如auth_id会对传入的数据进行数字验证，该验证早于validates
    def validate_auth(self, data):
        if not data:
            raise ValidationError("权限id不允许为空字符串。")
        if not isinstance(data, int):
            raise ValidationError("权限id必须为整数。")

    @pre_load
    def process_input(self, data, **kwargs):
        '''设置在验证数据之后将邮箱字段的值全部转小写，并去除前后空格。'''
        if data.get('email'):
            data['email'] = data.get('email').lower().strip()
        # if data.get('auth_id') and not isinstance(data.get('auth_id'), int): # 这里 可以做部分验证，实在找不到好的验证方法时
        #     raise ValidationError("权限id必须为整数。")
        return data


class CrudUseReturnUserSchema(CrudBaseSchema):
    id = fields.Int(dump_only=True)
    username = fields.String(label='用户名', dump_only=True)
    # password = fields.String(label='密码', dump_only=True)
    mobile = fields.String(label='手机号或电话', dump_only=True)
    email = fields.String(label='邮箱', dump_only=True)
    real_name = fields.String(label='真实姓名', dump_only=True)
    nick_name = fields.String(label='昵称', dump_only=True)
    region = fields.String(label='区域', dump_only=True)
    # avatar_url = fields.String(label='头像地址', dump_only=True)
    avatar_url = fields.String(label='头像地址', dump_only=True)
    gender = fields.Integer(label='性别', dump_only=True)
    birth_date = fields.Date(label='出生日期', format="%Y-%m-%d", dump_only=True)
    # group_id = fields.Integer(label='用户组', dump_only=True)
    group = fields.Nested(UserUseGroupSchema(exclude=("update_time", "create_time")), dump_only=True)
    auth_id = fields.Integer(label='权限', dump_only=True)