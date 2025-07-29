import logging
from typing import Self
from dataclasses import dataclass
from abc import ABC
from dateutil.parser import parse as dt_parse

logger = logging.getLogger(__name__)

class UnknownArgError(Exception): ...

class UnknownFieldError(Exception): ...

class QueryTypeError(Exception): ...

class ContextError(Exception): ...

class ArgParserConflictError(ContextError): ...

class ContextFieldConflictError(ContextError): ...

class ContextTableConflictError(ContextError): ...

class ContextRootTableError(ContextError): ...

class ContextTableResolutionError(ContextError): ...

class QueryType:
    numeric = "numeric"
    boolean = "boolean"
    text = "text"
    date = "date"
    null = "null"
    condition = "condition"
    select = "select"
    update = "update"
    insert = "insert"
    delete = "delete"
    where = "where"
    orderby = "orderby"

    value_types = {
        "numeric",
        "boolean",
        "text",
        "date",
        "null",
    }


@dataclass
class ContextField:
    alias: str
    source: str
    query_type: str
    depends_on: list[str]
    read_claim: str
    edit_claim: str
    filter_claim: str


@dataclass
class ContextTable:
    alias: str
    source: str
    join_condition: str
    depends_on: list[str]


class Context:
    def __init__(self, tables: list[ContextTable], fields: list[ContextField]):

        self.tables = dict()
        for t in tables:
            self._add_table(t)
        
        self.tables_order = []
        self._set_tables_order()

        self.fields = dict()
        for f in fields:
            self._add_field(f)

        # FIXME sub, mul, div, is_null, is_not_null, not, any?, orderby, update, insert, delete, limit, set
        self.arg_parsers = {
            "str": QueryStr,
            "date": QueryDate,
            "add": QueryAdd,
            "select": QuerySelect,
            "where": QueryWhere,
            "and": QueryAnd,
            "or": QueryOr,
            "eq": QueryEq,
            
        }

    def _add_field(self, field: ContextField):
        if field.alias in self.fields:
            raise ContextFieldConflictError(
                f"field.alias in self.fields {field.alias=}"
            )
        self.fields[field.alias] = field

    def _add_table(self, table: ContextTable):
        if table.alias in self.tables:
            raise ContextTableConflictError(
                f"table.alias in self.tables {table.alias=}"
            )

        self.tables[table.alias] = table
    
    def _set_tables_order(self):
        tables_order = []

        root_tables = {k for k, v in self.tables.items() if not v.depends_on}
        if len(root_tables) != 1:
            raise ContextRootTableError(f"len(root_tables) != 1 {root_tables=}")
        
        tables_order.append(list(root_tables)[0])
        remaining_tables = set(self.tables) - root_tables
        resolved_tables = set(root_tables)

        
        while len(remaining_tables) > 0:
            continue_resolve = False
            for table_alias in list(remaining_tables):
                table = self.tables[table_alias]
                depends_on = set(table.depends_on)
                if depends_on.issubset(resolved_tables):
                    tables_order.append(table_alias)
                    resolved_tables.add(table_alias)
                    remaining_tables.discard(table_alias)
                    continue_resolve = True
            if not continue_resolve:
                raise ContextTableResolutionError(f"_set_tables_order {remaining_tables=} {resolved_tables=}")

        self.tables_order = tables_order


    def add_arg_parser(
        self,
        query_id,
        query_cls,
    ):
        if query_id in self.arg_parsers:
            raise ArgParserConflictError(f"query_id in self.arg_parsers {query_id}")

        self.arg_parsers[query_id] = query_cls
    
    def parse_query(self, lq):
        q = Query(self, lq)
        return q
    
    def to_sql(self, lq):
        q = Query(self, lq)
        return q.to_sql()


def parse_arg(context, lq_arg):
    if lq_arg is None:
        return QueryNull()
    elif isinstance(lq_arg, float):
        return QueryFloat(lq_arg)
    elif isinstance(lq_arg, int):
        return QueryInt(lq_arg)
    elif isinstance(lq_arg, bool):
        return QueryBool(lq_arg)
    elif isinstance(lq_arg, str):
        return QueryField(context, lq_arg)
    elif isinstance(lq_arg, list):
        assert len(lq_arg) > 0
        q_id = lq_arg[0]
        arg = context.arg_parsers[q_id](context, lq_arg)
        return arg
    else:
        raise UnknownArgError(f"parse_arg error {lq_arg}")


def parse_args(context, lq_args):
    result = []
    for lq_arg in lq_args:
        q_arg = parse_arg(context, lq_arg)
        result.append(q_arg)
    return result


def assert_args_types(args, allowed_types: set):
    for arg in args:
        arg_query_type = arg.query_type()
        if arg_query_type not in allowed_types:
            raise QueryTypeError(
                f"assert_args_types {arg=} {arg_query_type=} {allowed_types=}"
            )


def assert_args_types_equal(args):
    if len(args) < 2:
        return

    query_types = {a.query_type() for a in args}
    if len(query_types) > 1:
        raise QueryTypeError(f"assert_args_types_equal {query_types=}")


def assert_args_contains_exactly_1(args, target_types):
    found_types = [a.query_type() for a in args if a.query_type() in target_types]
    if len(found_types) != 1:
        raise QueryTypeError(f"assert_args_contains_exactly_1 {found_types=}")
    
    return list(found_types)[0]

def assert_args_contains_at_most_1(args, target_types):
    found_types = [a.query_type() for a in args if a.query_type() in target_types]
    if len(found_types) > 1:
        raise QueryTypeError(f"assert_args_contains_at_most_1 {found_types=}")


def find_arg_by_type(args, target_type):
    for arg in args:
        if arg.query_type() == target_type:
            return arg

    return None


class QueryBase(ABC):
    args: list[Self] = []

    def to_sql(self):
        raise NotImplementedError("to_sql")

    def query_type(self):
        raise NotImplementedError("query_type")

    def collect_fields(self):
        result = set()
        for arg in self.args:
            result |= arg.collect_fields()
        return result
    
    def collect_read_claims(self, context):
        result = set()
        for arg in self.args:
            result |= arg.collect_read_claims(context)
        return result
        
    def collect_filter_claims(self, context):
        result = set()
        for arg in self.args:
            result |= arg.collect_filter_claims(context)
        return result
    
    def collect_edit_claims(self, context):
        result = set()
        for arg in self.args:
            result |= arg.collect_edit_claims(context)
        return result



class QueryFloat(QueryBase):
    def __init__(self, lq_arg):
        assert isinstance(lq_arg, float)
        self.value = lq_arg

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        param_name = f"param_{len(params)}"
        params[param_name] = self.value
        return f"%({param_name})s", params

    def query_type(self):
        return QueryType.numeric


class QueryInt(QueryBase):
    def __init__(self, lq_arg):
        assert isinstance(lq_arg, int)
        self.value = lq_arg

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        param_name = f"param_{len(params)}"
        params[param_name] = self.value
        return f"%({param_name})s", params

    def query_type(self):
        return QueryType.numeric


class QueryBool(QueryBase):
    def __init__(self, lq_arg):
        assert isinstance(lq_arg, bool)
        self.value = lq_arg

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        if self.value:
            return "TRUE", params
        else:
            return "FALSE", params

    def query_type(self):
        return QueryType.boolean


class QueryNull(QueryBase):
    def __init__(self):
        pass

    def to_sql(self, params=None):
        if params is None:
            params = dict()
        return "NULL", params

    def query_type(self):
        return QueryType.null


class QueryStr(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "str"
        assert isinstance(lq[1], str)
        self.value = lq[1]

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        param_name = f"param_{len(params)}"
        params[param_name] = self.value
        return f"%({param_name})s", params

    def query_type(self):
        return QueryType.text


class QueryDate(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "date"
        assert isinstance(lq[1], str)
        # FIXME allow specify unix epoch?
        self.value = dt_parse(lq[1])

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        param_name = f"param_{len(params)}"
        params[param_name] = self.value
        return f"%({param_name})s", params

    def query_type(self):
        return QueryType.date


class QuerySelect(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) > 1
        assert lq[0] == "select"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(
            args,
            QueryType.value_types,
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"SELECT {', '.join(args_sql)}", params

    def query_type(self):
        return QueryType.select

    def collect_edit_claims(self, context):
        return set()
    
    def collect_filter_claims(self, context):
        return set()


class QueryAdd(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) > 1
        assert lq[0] == "add"
        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(
            args,
            {
                QueryType.numeric,
                QueryType.null,
            },
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"({' + '.join(args_sql)})", params

    def query_type(self):
        return QueryType.numeric


class QueryField(QueryBase):
    def __init__(self, context, lq_arg):
        if lq_arg not in context.fields:
            raise UnknownFieldError(f"lq_arg not in context.fields {lq_arg=}")

        self.source = context.fields[lq_arg].source
        self.alias = lq_arg
        self.field_query_type = context.fields[lq_arg].query_type

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        return self.source, params

    def query_type(self):
        return self.field_query_type

    def collect_fields(self):
        return set([self.alias])

    def collect_read_claims(self, context):
        field = context.fields[self.alias]
        if field.read_claim:
            return set([field.read_claim])
        return set()
        
    def collect_filter_claims(self, context):
        field = context.fields[self.alias]
        if field.filter_claim:
            return set([field.filter_claim])
        return set()
    
    def collect_edit_claims(self, context):
        field = context.fields[self.alias]
        if field.edit_claim:
            return set([field.edit_claim])
        return set()

class QueryWhere(QueryBase):
    def __init__(
        self,
        context,
        lq,
    ):
        assert lq is not None
        assert lq[0] == "where"

        if len(lq) == 1:
            self.args = []
            return

        assert len(lq) == 2

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(
            args,
            {QueryType.condition},
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        if len(self.args) == 0:
            return ""

        sql, _ = self.args[0].to_sql(params)
        return f"WHERE {sql}", params

    def query_type(self):
        return QueryType.where

    def collect_edit_claims(self, context):
        return set()

class QueryAnd(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) > 1
        assert lq[0] == "and"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(
            args,
            {QueryType.condition},
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"({' AND '.join(args_sql)})", params

    def query_type(self):
        return QueryType.condition


class QueryOr(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) > 1
        assert lq[0] == "or"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(
            args,
            {QueryType.condition},
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"({' OR '.join(args_sql)})", params

    def query_type(self):
        return QueryType.condition


class QueryEq(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 3
        assert lq[0] == "eq"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(args, QueryType.value_types)
        assert_args_types_equal(args)
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        sql_1, _ = self.args[1].to_sql(params)
        return f"({sql_0} = {sql_1})", params

    def query_type(self):
        return QueryType.condition


class Query(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        args = parse_args(context, lq)

        self.context = context
        self.query_type = assert_args_contains_exactly_1(
            args,
            {
                QueryType.select,
                QueryType.update,
                QueryType.insert,
                QueryType.delete,
            },
        )
        self.select = None
        self.update = None
        self.insert = None
        self.delete = None
        self.where = None
        self.orderby = None

        if self.query_type == QueryType.select:
            assert_args_contains_at_most_1(
                args,
                {QueryType.where},
            )
            assert_args_contains_at_most_1(
                args,
                {QueryType.orderby},
            )
            self.select = find_arg_by_type(args, QueryType.select)
            self.where = find_arg_by_type(args, QueryType.where)
            self.orderby = find_arg_by_type(args, QueryType.orderby)
            self.args = args
            return
        else:
            raise NotImplementedError(f"not implemented {self.query_type=}")

    def collect_read_fields(self):
        result = set()
        if self.select is not None:
            result |= self.select.collect_fields()

        if self.where is not None:
            result |= self.where.collect_fields()

        if self.orderby is not None:
            result |= self.orderby.collect_fields()

        return result

    def collect_edit_fields(self):
        result = set()
        if self.update is not None:
            result |= self.update.collect_fields()

        return result

    def collect_filter_fields(self):
        result = set()

        if self.where is not None:
            result |= self.where.collect_fields()

        if self.orderby is not None:
            result |= self.orderby.collect_fields()

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        if self.query_type == QueryType.select:
            select_part, _ = self.select.to_sql(params)
            where_part = ""
            if self.where is not None:
                where_part, _ = self.where.to_sql(params)
            orderby_part = ""
            if self.orderby is not None:
                orderby_part, _ = self.orderby.to_sql(params)
            from_part = self.build_from_clause()
            parts = [select_part, from_part, where_part, orderby_part]
            parts = [p for p in parts if p]
            return "\n".join(parts) + ";", params

        else:
            raise NotImplementedError(f"not implemented {self.query_type=}")

    def get_required_tables(self):
        fields = self.collect_fields()
        fields = [self.context.fields[f] for f in fields]
        tables = set()
        for field in fields:
            for table_alias in field.depends_on:
                tables.add(table_alias)

        tables = [self.context.tables[t] for t in tables]
        required_tables = set()
        for table in tables:
            required_tables.add(table.alias)
            for table_alias in table.depends_on:
                required_tables.add(table_alias)

        return required_tables

    def build_from_clause(self):
        required_tables = self.get_required_tables()
        root_table = self.context.tables_order[0]
        root_table = self.context.tables[root_table]
        if len(required_tables) == 0:
            return f"FROM {root_table.source} {root_table.alias}"

        from_clause = f"FROM {root_table.source} {root_table.alias}"
        required_tables -= {root_table.alias}
        for table_alias in self.context.tables_order:
            if table_alias not in required_tables:
                continue

            table = self.context.tables[table_alias]
            from_clause += f"\nLEFT JOIN {table.source} {table.alias} ON {table.join_condition}"
        
        return from_clause

    def get_required_claims(self):
        result = set()
        result |= self.collect_read_claims(self.context)
        result |= self.collect_filter_claims(self.context)
        result |= self.collect_edit_claims(self.context)
        return result
        
