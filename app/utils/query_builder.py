from flask_sqlalchemy.query import Query
from sqlalchemy import asc, desc


class QueryBuilder:
    query: Query

    def __init__(self, query: Query):
        self.query = query

    def filter_if(self, condition, criterion_fn):
        if condition:
            self.query = self.query.filter(criterion_fn())
        return self

    def sort(self, model, sort_by, sort_order):
        col = getattr(model, sort_by)
        self.query = self.query.order_by(
            desc(col) if sort_order == "desc" else asc(col)
        )
        return self

    def build(self):
        return self.query
