from flask_sqlalchemy.query import Query
from sqlalchemy import asc, desc, func


class QueryBuilder:
    query: Query

    def __init__(self, query: Query):
        self.query = query

    def filter_if(self, condition, criterion_fn):
        if condition:
            self.query = self.query.filter(criterion_fn())
        return self

    def search(self, condition, model):
        if not condition:
            return self

        search_query = func.websearch_to_tsquery("english", condition)

        self.query = self.query.filter(model.search_vector.op("@@")(search_query))

        rank = func.ts_rank(model.search_vector, search_query)
        self.query = self.query.order_by(desc(rank))

        return self

    def sort(self, model, sort_by, sort_order):
        col = getattr(model, sort_by)
        self.query = self.query.order_by(
            desc(col) if sort_order == "desc" else asc(col)
        )
        return self

    def build(self):
        return self.query
