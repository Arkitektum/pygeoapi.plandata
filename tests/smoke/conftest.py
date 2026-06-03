# =================================================================
#
# Fork-gated smoke tests for per-dataset GML output-formatter dispatch.
#
# These exercise the real chain that production runs:
#   postgres -> postgresql_ext (property_shape: dotted + gml_passthrough)
#   -> get_collection_item(s) handler -> ReguleringsplanFormatter -> GML
#
# They require a live postgres AND the Arkitektum packages, which are NOT
# in the default dev/CI environment (installing them in the main test job
# would create the circular dependency the project README/CLAUDE.md warns
# about). The importorskip calls below short-circuit collection cleanly
# when those deps are absent, so a bare `pytest` is unaffected; the smoke
# CI job (.github/workflows/smoke.yml) installs requirements-smoke.txt and
# runs `pytest tests/smoke`.
#
# A red smoke run means a FORK regression in the dispatch contract — the
# formatter and provider are pinned to released tags (v0.2.0 / v0.4.0), so
# they cannot move underneath this test.
#
# =================================================================

import os
import pathlib

import pytest

pytestmark = pytest.mark.smoke

# psycopg (v3) loads schema/fixtures directly. postgresql_ext additionally
# imports osgeo (GDAL bindings) at module top — `pip install gdal` is not
# enough, the system needs libgdal first (the smoke workflow installs it).
psycopg = pytest.importorskip(
    'psycopg',
    reason='smoke tests require psycopg (see requirements-smoke.txt)'
)
pytest.importorskip(
    'postgresql_ext',
    reason='smoke requires postgresql_ext + GDAL (see smoke.yml)'
)
pytest.importorskip(
    'pygeoapi_formatter_gml_npad',
    reason='smoke requires the gml-npad formatter (requirements-smoke.txt)'
)

from pygeoapi.api import API  # noqa: E402
from pygeoapi.util import yaml_load  # noqa: E402

from tests.util import get_test_file_path  # noqa: E402

_HERE = pathlib.Path(__file__).parent

# Connection params follow the fork's existing postgres-test convention
# (tests/provider/test_postgresql_provider.py): host 127.0.0.1, db 'test',
# user 'postgres', password from POSTGRESQL_PASSWORD.
DB = {
    'host': os.environ.get('POSTGRESQL_HOST', '127.0.0.1'),
    'port': int(os.environ.get('POSTGRESQL_PORT', '5432')),
    'dbname': os.environ.get('POSTGRESQL_DBNAME', 'test'),
    'user': os.environ.get('POSTGRESQL_USER', 'postgres'),
    'password': os.environ.get('POSTGRESQL_PASSWORD', 'postgres'),
}


def _conn_str() -> str:
    return (
        f"host={DB['host']} port={DB['port']} dbname={DB['dbname']} "
        f"user={DB['user']} password={DB['password']}"
    )


@pytest.fixture(scope='session', autouse=True)
def smoke_db():
    """Load the vendored schema + fixtures once per session."""
    schema_sql = (_HERE / 'schema.sql').read_text(encoding='utf-8')
    fixtures_sql = (_HERE / 'fixtures.sql').read_text(encoding='utf-8')
    with psycopg.connect(_conn_str(), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
            cur.execute(fixtures_sql)
    yield


def _rpomrade_resource() -> dict:
    return {
        'type': 'collection',
        'title': 'RpOmråde smoke',
        'description': 'Reguleringsplan område smoke collection',
        'keywords': ['smoke'],
        'extents': {
            'spatial': {
                'bbox': [4.0, 57.0, 32.0, 72.0],
                'crs': 'http://www.opengis.net/def/crs/OGC/1.3/CRS84',
            }
        },
        'providers': [{
            'type': 'feature',
            'name': 'postgresql_ext.PostgreSQLExtendedProvider',
            # property_shape: dotted is the contract the formatter requires
            # (postgresql_ext v0.3.0+); gml_passthrough injects _geometry_gml
            # as a server-side ST_AsGML column (v0.4.0+).
            'property_shape': 'dotted',
            'gml_passthrough': True,
            'data': {
                'host': DB['host'],
                'port': DB['port'],
                'dbname': DB['dbname'],
                'user': DB['user'],
                'password': DB['password'],
                'search_path': ['public'],
            },
            'id_field': 'objid',
            'table': 'rpomrade_omrade_mv',
            'geom_field': 'område',
        }],
        'formatters': [{
            'name': 'pygeoapi_formatter_gml_npad.reguleringsplan_20190401.ReguleringsplanFormatter',  # noqa: E501
            'feature_type': 'RpOmråde',
            # XSD validation needs egress to skjema.geonorge.no; the routing
            # contract under test here does not depend on it. XSD correctness
            # is covered by the formatter repo's own smoke.
            'validate': False,
            'f': 'gml',
            'mimetype': 'application/gml+xml',
        }],
    }


@pytest.fixture()
def smoke_api():
    """An API with one postgres-backed, GML-formatter-wired collection.

    openapi is unused by the item handlers, so {} suffices.
    """
    with open(get_test_file_path('pygeoapi-test-config.yml')) as fh:
        config = yaml_load(fh)
    config['resources'] = {'rpomrade': _rpomrade_resource()}
    return API(config, {})
