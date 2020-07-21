from marshmallow import Schema, fields, EXCLUDE


class BaseSchema(Schema):
    create_time = fields.DateTime("%Y-%m-%d %H:%M:%S", dump_only=True)
    update_time = fields.DateTime("%Y-%m-%d %H:%M:%S", dump_only=True)

    class Meta:
        unknown = EXCLUDE # 对位置字段的处理：EXCLUDE: 直接扔掉位置字段；INCLUDE: 接受未知字段；RAISE: 抛出异常，默认的，当传入不需要的字段时会直接抛出异常