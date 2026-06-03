# =================================================================
#
# Smoke: per-dataset GML formatter dispatch on the items + single-item
# routes, end to end through postgres and the real formatter.
#
# See tests/smoke/conftest.py for what these require and why they live in
# the fork (failure attribution: red == fork dispatch regression).
#
# =================================================================

from http import HTTPStatus

import pytest

from pygeoapi.api.itemtypes import get_collection_item, get_collection_items

from tests.util import mock_api_request

pytestmark = pytest.mark.smoke


def _as_text(content) -> str:
    return content.decode('utf-8') if isinstance(content, bytes) else content


def test_items_route_dispatches_gml(smoke_api):
    req = mock_api_request({'f': 'gml'})
    headers, code, content = get_collection_items(smoke_api, req, 'rpomrade')

    assert code == HTTPStatus.OK
    assert headers['Content-Type'] == 'application/gml+xml'

    gml = _as_text(content)
    assert '<wfs:FeatureCollection ' in gml
    assert 'numberReturned="1"' in gml
    assert gml.count('<app:RpOmråde ') == 1
    assert '<app:lokalId>rp-smoke-001</app:lokalId>' in gml


def test_single_item_route_dispatches_gml(smoke_api):
    req = mock_api_request({'f': 'gml'})
    headers, code, content = get_collection_item(
        smoke_api, req, 'rpomrade', '1')

    assert code == HTTPStatus.OK
    assert headers['Content-Type'] == 'application/gml+xml'
    assert headers['Content-Disposition'] == 'attachment; filename="rpomrade.gml"'  # noqa: E501

    gml = _as_text(content)
    # the single feature is wrapped as a one-member wfs:FeatureCollection
    assert '<wfs:FeatureCollection ' in gml
    assert 'numberReturned="1"' in gml
    assert gml.count('<app:RpOmråde ') == 1
    assert '<app:lokalId>rp-smoke-001</app:lokalId>' in gml
    # geometry came through gml_passthrough into the XSD-ordered wrapper
    assert '<app:område>' in gml


def test_single_item_json_still_default(smoke_api):
    # the dispatch branch must not shadow the default GeoJSON path
    req = mock_api_request()
    headers, code, content = get_collection_item(
        smoke_api, req, 'rpomrade', '1')

    assert code == HTTPStatus.OK
    import json
    feature = json.loads(_as_text(content))
    assert feature['type'] == 'Feature'
    # alternate link advertises f=gml, not the plugin name
    gml_links = [li for li in feature['links']
                 if li.get('type') == 'application/gml+xml']
    assert len(gml_links) == 1
    assert gml_links[0]['href'].endswith('?f=gml')
