import logging
from http import HTTPStatus
from typing import Dict, List, Tuple, Any
from pygeoapi.plugin import load_plugin
from pygeoapi.util import (filter_providers_by_type,
                           filter_dict_by_key_value, to_json)
from pygeoapi.provider.base import ProviderGenericError
from . import APIRequest, API, SYSTEM_LOCALE

LOGGER = logging.getLogger(__name__)

CONFORMANCE_CLASSES_STYLES = [
    'http://www.opengis.net/spec/ogcapi-styles-1/0.0/conf/core',
    'http://www.opengis.net/spec/ogcapi-styles-1/0.0/conf/mapbox-styles',
    # 'http://www.opengis.net/spec/ogcapi-styles-1/0.0/conf/sld-10',
    # 'http://www.opengis.net/spec/ogcapi-styles-1/0.0/conf/sld-11',
    # 'http://www.opengis.net/spec/ogcapi-styles-1/0.0/conf/style-info'
]


class BaseStyleProvider():
    def get_styles(self) -> Dict[str, Any]:
        raise NotImplementedError()

    def get_style(self, style_id: str) -> Dict[str, Any] | None:
        raise NotImplementedError()

    def get_style_metadata(self, style_id: str) -> Dict[str, Any] | None:
        raise NotImplementedError()

    def get_style_definition(self, style_id: str, format_: str) -> str | None:
        raise NotImplementedError()

    def get_style_preview(self, style_id: str):
        raise NotImplementedError()


def get_styles(api: API, request: APIRequest) -> Tuple[Dict, int, str]:
    headers = request.get_response_headers(SYSTEM_LOCALE, **api.api_headers)

    provider_defs = _get_provider_defs(api)
    server_url = api.config['server']['url']
    styles: List[Dict] = []

    for provider_def in provider_defs:
        try:
            plugin = _load_plugin(provider_def, server_url)
            content = plugin.get_styles()
            styles.extend(content['styles'])
        except ProviderGenericError as err:
            return api.get_exception(
                err.http_status_code, headers, request.format,
                err.ogc_exception_code, err.message)

    content = {
        'styles': styles,
        'links': [
            {
                'rel': 'alternate',
                'type': 'text/html',
                'title': 'This document as HTML',
                'href': f'{server_url}/styles?f=html'
            },
            {
                'rel': 'self',
                'type': 'application/json',
                'title': 'This document',
                'href': f'{server_url}/styles?f=json'
            }
        ]
    }

    # if request.format == F_HTML:
    #     html = render_j2_template(
    #         api.tpl_config, api.config['server']['templates'],
    #         'styles/index.jinja2', content, str(request.locale))

    #     return headers, HTTPStatus.OK, html

    return headers, HTTPStatus.OK, to_json(content, api.pretty_print)


def get_collection_styles(api: API, request: APIRequest,
                          collection_id: str) -> Tuple[Dict, int, str]:
    headers = request.get_response_headers(SYSTEM_LOCALE, **api.api_headers)

    collections = filter_dict_by_key_value(
        api.config['resources'], 'type', 'collection')

    collection = collections.get(collection_id)

    if not collection:
        return api.get_exception(
            HTTPStatus.NOT_FOUND, headers, request.format,
            'NotFound', 'Collection not found')

    provider_def = filter_providers_by_type(collection['providers'], 'style')

    if not provider_def:
        return api.get_exception(
            HTTPStatus.NOT_FOUND, headers, request.format,
            'NotFound', 'Style not found')

    server_url = api.config['server']['url']

    try:
        plugin = _load_plugin(provider_def, server_url)
    except ProviderGenericError as err:
        return api.get_exception(
            err.http_status_code, headers, request.format,
            err.ogc_exception_code, err.message)

    content = plugin.get_styles()

    content['links'] = [
        {
            'rel': 'alternate',
            'type': 'text/html',
            'title': 'This document as HTML',
            'href': f'{server_url}/collections/{collection_id}/styles?f=html'
        },
        {
            'rel': 'self',
            'type': 'application/json',
            'title': 'This document',
            'href': f'{server_url}/collections/{collection_id}/styles?f=json'
        }
    ]

    # if request.format == F_HTML:
    #     return headers, HTTPStatus.OK, '<h1>Test</h1>'

    return headers, HTTPStatus.OK, to_json(content, api.pretty_print)


def get_style(api: API, request: APIRequest,
              style_id: str) -> Tuple[dict, int, str]:
    headers = request.get_response_headers(SYSTEM_LOCALE, **api.api_headers)

    provider_def = _get_provider_def(api, style_id)

    if not provider_def:
        return api.get_exception(
            HTTPStatus.NOT_FOUND, headers, request.format,
            'NotFound', 'Style not found')

    server_url = api.config['server']['url']

    try:
        plugin = _load_plugin(provider_def, server_url)
    except ProviderGenericError as err:
        return api.get_exception(
            err.http_status_code, headers, request.format,
            err.ogc_exception_code, err.message)

    content = plugin.get_style(style_id)

    if not content:
        return api.get_exception(
            HTTPStatus.NOT_FOUND, headers, request.format,
            'NotFound', 'Style not found')

    # if request.format == F_HTML:
    #     return headers, HTTPStatus.OK, '<h1>Test</h1>'

    return headers, HTTPStatus.OK, to_json(content, api.pretty_print)


def get_style_definition(api: API, request: APIRequest,
                         style_id: str) -> Tuple[dict, int, str]:
    headers = request.get_response_headers(SYSTEM_LOCALE, **api.api_headers)

    provider_def = _get_provider_def(api, style_id)

    if not provider_def:
        return api.get_exception(
            HTTPStatus.NOT_FOUND, headers, request.format,
            'NotFound', 'Style not found')

    server_url = api.config['server']['url']

    try:
        plugin = _load_plugin(provider_def, server_url)
    except ProviderGenericError as err:
        return api.get_exception(
            err.http_status_code, headers, request.format,
            err.ogc_exception_code, err.message)

    content = plugin.get_style_definition(style_id, str(request.format))

    if not content:
        return api.get_exception(
            HTTPStatus.NOT_FOUND, headers, request.format,
            'NotFound', 'Style not found')

    # if request.format == F_HTML:
    #     return headers, HTTPStatus.OK, '<h1>Test</h1>'

    return headers, HTTPStatus.OK, content


def get_style_metadata(api: API, request: APIRequest,
                       style_id: str) -> Tuple[dict, int, str]:
    headers = request.get_response_headers(SYSTEM_LOCALE, **api.api_headers)

    provider_def = _get_provider_def(api, style_id)

    if not provider_def:
        return api.get_exception(
            HTTPStatus.NOT_FOUND, headers, request.format,
            'NotFound', 'Style not found')

    server_url = api.config['server']['url']

    try:
        plugin = _load_plugin(provider_def, server_url)
    except ProviderGenericError as err:
        return api.get_exception(
            err.http_status_code, headers, request.format,
            err.ogc_exception_code, err.message)

    content = plugin.get_style_metadata(style_id)

    if not content:
        return api.get_exception(
            HTTPStatus.NOT_FOUND, headers, request.format,
            'NotFound', 'Style not found')

    if 'links' not in content:
        content['links'] = []

    content['links'].extend([
        {
            'rel': 'alternate',
            'type': 'text/html',
            'title': 'This document as HTML',
            'href': f'{server_url}/styles/{style_id}/metadata?f=html'
        },
        {
            'rel': 'self',
            'type': 'application/json',
            'title': 'This document',
            'href': f'{server_url}/styles/{style_id}/metadata?f=json'
        }
    ])

    # if request.format == F_HTML:
    #     return headers, HTTPStatus.OK, '<h1>Test</h1>'

    return headers, HTTPStatus.OK, to_json(content, api.pretty_print)


def get_oas_30(
        cfg: Dict, locale: str
) -> Tuple[List[Dict[str, str]], Dict[str, Dict]]:
    return [], {'paths': {}}


def _get_provider_def(api: API, style_id: str) -> Dict | None:
    provider_defs = _get_provider_defs(api)

    for provider_def in provider_defs:
        if _has_style_id(provider_def, style_id):
            return provider_def

    return None


def _get_provider_defs(api: API) -> List[Dict]:
    provider_defs = []

    global_styles = filter_dict_by_key_value(
        api.config['resources'], 'type', 'styles')

    if global_styles:
        provider_defs.append(global_styles['styles']['provider'])

    collections = filter_dict_by_key_value(
        api.config['resources'], 'type', 'collection')

    for key in collections.keys():
        provider_def = filter_providers_by_type(
            collections[key]['providers'], 'style')

        if provider_def:
            provider_defs.append(provider_def)

    return provider_defs


def _has_style_id(provider_def: Dict | None, style_id: str) -> bool:
    if not provider_def:
        return False

    styles = provider_def['styles']
    has_style_id = any(style['id'] == style_id for style in styles)

    return has_style_id


def _load_plugin(provider_def: Dict, server_url: str) -> BaseStyleProvider:
    provider_def['server_url'] = server_url

    return load_plugin('provider', provider_def)
