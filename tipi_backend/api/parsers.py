import re
from webargs import fields

from tipi_backend.api.managers.initiative_type import InitiativeTypeManager


detail_args = {
        'id': fields.String(required=True,location='view_args')
        }

search_initiatives_args = {
        'topic': fields.String(missing=""),
        'tags': fields.List(fields.Str(), missing=list),
        'author': fields.String(missing=""),
        'startdate': fields.Date(missing=None),
        'enddate': fields.Date(missing=None),
        'place': fields.String(missing=""),
        'reference': fields.String(missing=""),
        'type': fields.String(missing=""),
        'state': fields.String(missing=""),
        'title': fields.String(missing=""),
        }



class SearchInitiativeParser:

    class DefaultParser():
        @staticmethod
        def get_search_for(key, value):
            return {key: value}

    class TitleParser():
        @staticmethod
        def get_search_for(key, value):
            return {key: {'$regex': value, '$options': 'gi'}}

    class TypeParser():
        @staticmethod
        def get_search_for(key, value):
            return InitiativeTypeManager().get_search_for(value)

    class TopicParser():
        @staticmethod
        def get_search_for(key, value):
            return {'topics': value}

    class TagParser():
        @staticmethod
        def get_search_for(key, value):
            return {'tags': {'$elemMatch': {'tag': value}}}

    parser_by_params = {
            'topic': TopicParser,
            'tags': TagParser,
            'author': DefaultParser,
            'startdate': DefaultParser,
            'enddate': DefaultParser,
            'place': DefaultParser,
            'reference': DefaultParser(),
            'type': TypeParser(),
            'state': DefaultParser(),
            'title': TitleParser(),
            }

    def __init__(self, params):
        self._params = params.to_dict()
        self._limit = self._return_attr_in_params(attrname='limit', type=int, default=20, clean=True)
        self._offset = self._return_attr_in_params(attrname='offset', type=int, default=0, clean=True)
        self._parse_params(self._params)

    def _parse_params(self, params):
        temp_params = params.copy()
        for key, value in temp_params.items():
            del params[key]
            params.update(self.parser_by_params[key].get_search_for(key, value))

    def _return_attr_in_params(self, attrname='', type=str, default='', clean=False):
        if attrname in self._params:
            attr = self._params[attrname]
            if clean:
                self._clean_params_for_attr(attrname)
            return type(attr)
        return default

    def _clean_params_for_attr(self, attrname=''):
        if attrname in self._params:
            self._params.pop(attrname)

    @property
    def limit(self):
        return self._limit

    @property
    def offset(self):
        return self._offset

    @property
    def params(self):
        return self._params


