from marshmallow import Schema, fields, validate


class PaginationSchema(Schema):
    total = fields.Int()
    pages = fields.Int()
    page = fields.Int()
    per_page = fields.Int()


class PaginationQuerySchema(Schema):
    page = fields.Int(load_default=1)
    per_page = fields.Int(load_default=20, validate=validate.Range(max=100))
