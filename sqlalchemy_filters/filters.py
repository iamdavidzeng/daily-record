# -*- coding: utf-8 -*-
from collections import Iterable, namedtuple
from inspect import signature
from itertools import chain

from six import string_types
from sqlalchemy import and_, or_, not_

from .exceptions import BadFilterFormat
from .models import Field, get_model_from_spec


BooleanFunction = namedtuple(
    'BooleanFunction', ('key', 'sqlalchemy_fn', 'only_one_arg')
)
BOOLEAN_FUNCTIONS = [
    BooleanFunction('or', or_, False),
    BooleanFunction('and', and_, False),
    BooleanFunction('not', not_, True),
]
"""
Sqlalchemy boolean functions that can be parsed from the filter definition.
"""


class Operator(object):

    OPERATORS = {
        'is_null': lambda f: f.is_(None),
        'is_not_null': lambda f: f.isnot(None),
        '==': lambda f, a: f == a,
        'eq': lambda f, a: f == a,
        '!=': lambda f, a: f != a,
        'ne': lambda f, a: f != a,
        '>': lambda f, a: f > a,
        'gt': lambda f, a: f > a,
        '<': lambda f, a: f < a,
        'lt': lambda f, a: f < a,
        '>=': lambda f, a: f >= a,
        'ge': lambda f, a: f >= a,
        '<=': lambda f, a: f <= a,
        'le': lambda f, a: f <= a,
        'like': lambda f, a: f.like(a),
        'in': lambda f, a: f.in_(a),
        'not_in': lambda f, a: ~f.in_(a),
    }

    def __init__(self, operator=None):
        if not operator:
            operator = '=='

        if operator not in self.OPERATORS:
            raise BadFilterFormat('Operator `{}` not valid.'.format(operator))

        self.operator = operator
        self.function = self.OPERATORS[operator]
        self.arity = len(signature(self.function).parameters)


class Filter(object):

    def __init__(self, filter_spec):
        self.filter_spec = filter_spec

    def format_for_sqlalchemy(self, query):
        filter_spec = self.filter_spec

        try:
            field_name = filter_spec['field']
        except KeyError:
            raise BadFilterFormat('`field` is a mandatory filter attribute.')
        except TypeError:
            raise BadFilterFormat(
                'Filter spec `{}` should be a dictionary.'.format(filter_spec)
            )

        model = get_model_from_spec(filter_spec, query)

        operator = Operator(filter_spec.get('op'))
        value = filter_spec.get('value')
        value_present = True if 'value' in filter_spec else False
        if not value_present and operator.arity == 2:
            raise BadFilterFormat('`value` must be provided.')

        function = operator.function
        arity = operator.arity

        field = Field(model, field_name)
        sqlalchemy_field = field.get_sqlalchemy_field()

        if arity == 1:
            return function(sqlalchemy_field)

        if arity == 2:
            return function(sqlalchemy_field, value)


class BooleanFilter:

    def __init__(self, function, *filters):
        self.function = function
        self.filters = filters

    def format_for_sqlalchemy(self, query):
        return self.function(
            *[filter.format_for_sqlalchemy(query) for filter in self.filters]
        )


def _is_iterable_filter(filter_spec):
    """ `filter_spec` may be a list of nested filter specs, or a dict.
    """
    return (
        isinstance(filter_spec, Iterable) and
        not isinstance(filter_spec, (string_types, dict))
    )


def build_filters(filter_spec):
    """ Recursively process `filter_spec` """

    if _is_iterable_filter(filter_spec):
        return list(chain.from_iterable(
            build_filters(item) for item in filter_spec
        ))

    if isinstance(filter_spec, dict):
        # Check if filter spec defines a boolean function.
        for boolean_function in BOOLEAN_FUNCTIONS:
            if boolean_function.key in filter_spec:
                # The filter spec is for a boolean-function
                # Get the function argument definitions and validate
                fn_args = filter_spec[boolean_function.key]

                if not _is_iterable_filter(fn_args):
                    raise BadFilterFormat(
                        '`{}` value must be an iterable across the function '
                        'arguments'.format(boolean_function.key)
                    )
                if boolean_function.only_one_arg and len(fn_args) != 1:
                    raise BadFilterFormat(
                        '`{}` must have one argument'.format(
                            boolean_function.key
                        )
                    )
                if not boolean_function.only_one_arg and len(fn_args) < 1:
                    raise BadFilterFormat(
                        '`{}` must have one or more arguments'.format(
                            boolean_function.key
                        )
                    )
                return [
                    BooleanFilter(
                        boolean_function.sqlalchemy_fn, *build_filters(fn_args)
                    )
                ]

    return [Filter(filter_spec)]


def apply_filters(query, filter_spec):
    """Apply filters to a SQLAlchemy query.

    :param query:
        A :class:`sqlalchemy.orm.Query` instance.

    :param filter_spec:
        A dict or an iterable of dicts, where each one includes
        the necesary information to create a filter to be applied to the
        query.

        Example::

            filter_spec = [
                {'model': 'Foo', 'field': 'name', 'op': '==', 'value': 'foo'},
            ]

        If the query being modified refers to a single model, the `model` key
        may be omitted from the filter spec.

        Filters may be combined using boolean functions.

        Example:

            filter_spec = {
                'or': [
                    {'model': 'Foo', 'field': 'id', 'op': '==', 'value': '1'},
                    {'model': 'Bar', 'field': 'id', 'op': '==', 'value': '2'},
                ]
            }

    :returns:
        The :class:`sqlalchemy.orm.Query` instance after all the filters
        have been applied.
    """
    filters = build_filters(filter_spec)
    sqlalchemy_filters = [
        filter.format_for_sqlalchemy(query) for filter in filters
    ]

    if sqlalchemy_filters:
        query = query.filter(*sqlalchemy_filters)

    return query
