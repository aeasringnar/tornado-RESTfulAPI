from marshmallow import Schema, fields, ValidationError, validate, validates, pre_load, validates_schema
from base.schema import BaseSchema


class GetMobielCoseSchema(BaseSchema):
    mobile = fields.String(label='手机号', required=True, error_messages={"required": "请输入手机号。"})