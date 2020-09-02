from marshmallow import Schema, fields, EXCLUDE


class CrudBaseSchema(Schema):

    class Meta:
        unknown = EXCLUDE