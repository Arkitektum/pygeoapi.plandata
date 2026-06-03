-- VENDORED VERBATIM from pygeoapi.formatter.gml-npad
--   source: tests/smoke/schema.sql @ tag v0.2.0
-- Do not edit here. The formatter repo flags schema changes in its
-- release notes; re-vendor on bump. See tests/smoke/conftest.py.
--
-- Minimal smoke-test schema for the SOSI GML formatter.
--
-- These are TABLEs (not MATERIALIZED VIEWs) for setup simplicity; postgresql_ext
-- treats them identically via SQLAlchemy reflection. The column set is the
-- minimum required for the serialized feature to pass XSD validation: every
-- REQUIRED element of RpOmrådeType / KpOmrådeType plus the nested wrappers
-- (identifikasjon / arealplanId / kopidata) and a few optional properties.
--
-- Diacritics and dots in column names are required by the SOSI / NPAD convention
-- and must be double-quoted. The geom column name differs between RP (`område`)
-- and KP (`geometri`) — matches gml-export's FeatureTypeConfig.geometry_column.
--
-- All value columns are text on purpose — production MVs may carry
-- zero-prefixed identifiers (e.g. kommunenummer '0301'), and the writer
-- stringifies values anyway. XSD numeric types (xs:integer for
-- kopidata.områdeId) accept leading zeros in their lexical space, so text
-- with integer-lexical content validates fine.
--
-- `_geometry_gml` is NOT a column: postgresql_ext v0.4.0's
-- `gml_passthrough: true` injects it as a server-side ST_AsGML
-- column_property at query time.

CREATE EXTENSION IF NOT EXISTS postgis;

DROP TABLE IF EXISTS rpomrade_omrade_mv CASCADE;
DROP TABLE IF EXISTS kpomrade_mv CASCADE;
DROP TABLE IF EXISTS rpformalgrense_grense_mv CASCADE;

-- Reguleringsplan: RpOmråde
CREATE TABLE rpomrade_omrade_mv (
    objid                              bigint PRIMARY KEY,
    "område"                           geometry(Polygon, 25833),
    "identifikasjon.lokalId"           text,
    "identifikasjon.navnerom"          text,
    "identifikasjon.versjonId"         text,
    "arealplanId.kommunenummer"        text,
    "arealplanId.landkode"             text,
    "arealplanId.planidentifikasjon"   text,
    "kopidata.områdeId"                text,
    "kopidata.originalDatavert"        text,
    "kopidata.kopidato"                date,
    "vertikalnivå"                     text,
    plantype                           text,
    planstatus                         text,
    plannavn                           text,
    planbestemmelse                    text,
    lovreferanse                       text
);

-- Reguleringsplan: RpFormålGrense — representative of all 29 grense
-- (boundary) types, which share one XSD shape: Fellesegenskaper_LinjerOgPunkt
-- base sequence (identifikasjon / dates / kvalitet / kopidata, NO arealplanId)
-- plus a single `grense` curve element.
CREATE TABLE rpformalgrense_grense_mv (
    objid                              bigint PRIMARY KEY,
    "grense"                           geometry(LineString, 25833),
    "identifikasjon.lokalId"           text,
    "identifikasjon.navnerom"          text,
    "identifikasjon.versjonId"         text,
    -- xs:dateTime in the XSD — timestamp (not date) so the serialized
    -- value carries the T00:00:00 part xs:dateTime requires
    "førsteDigitaliseringsdato"        timestamp,
    "oppdateringsdato"                 timestamp,
    "kvalitet.målemetode"              text,
    "kvalitet.nøyaktighet"             text,
    "kopidata.områdeId"                text,
    "kopidata.originalDatavert"        text,
    "kopidata.kopidato"                date
);

-- Kommuneplan: KpOmråde. Note `geometri` (not `område`) for the geom column —
-- matches the production MV column name in gml-export's FeatureTypeConfig.
CREATE TABLE kpomrade_mv (
    objid                              bigint PRIMARY KEY,
    "geometri"                         geometry(Polygon, 25833),
    "identifikasjon.lokalId"           text,
    "identifikasjon.navnerom"          text,
    "identifikasjon.versjonId"         text,
    "arealplanId.kommunenummer"        text,
    "arealplanId.landkode"             text,
    "arealplanId.planidentifikasjon"   text,
    "kopidata.områdeId"                text,
    "kopidata.originalDatavert"        text,
    "kopidata.kopidato"                date,
    plantype                           text,
    planstatus                         text,
    plannavn                           text,
    planbestemmelse                    text,
    lovreferanse                       text
);
