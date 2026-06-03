-- VENDORED VERBATIM from pygeoapi.formatter.gml-npad
--   source: tests/smoke/fixtures.sql @ tag v0.2.0
-- Do not edit here. Re-vendor on formatter bump.
--
-- Smoke-test fixtures: one row per table carrying every XSD-REQUIRED element
-- of RpOmrådeType / KpOmrådeType (so `validate: true` passes) plus the nested
-- groups. Polygon geometries are placeholder shapes near Oslo
-- (kommunenummer 0301). kopidata.områdeId is deliberately zero-prefixed to
-- lock the leading-zero survival path (text column, xs:integer lexical).
--
-- Code values per the 20190401 XSDs:
--   RP planstatus '4' is valid for RP; KP's PlanstatusEnumerationType only
--   allows 1|2|3, hence '3' on the KP row. planbestemmelse / lovreferanse
--   use code '1' on both.

TRUNCATE TABLE rpomrade_omrade_mv, kpomrade_mv, rpformalgrense_grense_mv;

INSERT INTO rpomrade_omrade_mv (
    objid,
    "område",
    "identifikasjon.lokalId",
    "identifikasjon.navnerom",
    "identifikasjon.versjonId",
    "arealplanId.kommunenummer",
    "arealplanId.landkode",
    "arealplanId.planidentifikasjon",
    "kopidata.områdeId",
    "kopidata.originalDatavert",
    "kopidata.kopidato",
    "vertikalnivå",
    plantype,
    planstatus,
    plannavn,
    planbestemmelse,
    lovreferanse
) VALUES (
    1,
    ST_GeomFromText('POLYGON((597000 6643000, 598000 6643000, 598000 6644000, 597000 6644000, 597000 6643000))', 25833),
    'rp-smoke-001',
    'https://data.geonorge.no/SOSI/produktspesifikasjon/Reguleringsplan/20190401',
    '1',
    '301',
    'NO',
    'rp-plan-0001',
    '0301',
    'Kartverket',
    '2019-04-01',
    '2',
    '35',
    '4',
    'Smoke Test Reguleringsplan',
    '1',
    '1'
);

INSERT INTO kpomrade_mv (
    objid,
    "geometri",
    "identifikasjon.lokalId",
    "identifikasjon.navnerom",
    "identifikasjon.versjonId",
    "arealplanId.kommunenummer",
    "arealplanId.landkode",
    "arealplanId.planidentifikasjon",
    "kopidata.områdeId",
    "kopidata.originalDatavert",
    "kopidata.kopidato",
    plantype,
    planstatus,
    plannavn,
    planbestemmelse,
    lovreferanse
) VALUES (
    1,
    ST_GeomFromText('POLYGON((598000 6644000, 599000 6644000, 599000 6645000, 598000 6645000, 598000 6644000))', 25833),
    'kp-smoke-001',
    'https://data.geonorge.no/SOSI/produktspesifikasjon/Kommuneplan/20190401',
    '1',
    '301',
    'NO',
    'kp-plan-0001',
    '0301',
    'Kartverket',
    '2019-04-01',
    '20',
    '3',
    'Smoke Test Kommuneplan',
    '1',
    '1'
);

INSERT INTO rpformalgrense_grense_mv (
    objid,
    "grense",
    "identifikasjon.lokalId",
    "identifikasjon.navnerom",
    "identifikasjon.versjonId",
    "førsteDigitaliseringsdato",
    "oppdateringsdato",
    "kvalitet.målemetode",
    "kvalitet.nøyaktighet",
    "kopidata.områdeId",
    "kopidata.originalDatavert",
    "kopidata.kopidato"
) VALUES (
    1,
    ST_GeomFromText('LINESTRING(597000 6643000, 598000 6643000, 598000 6644000)', 25833),
    'rpfg-smoke-001',
    'https://data.geonorge.no/SOSI/produktspesifikasjon/Reguleringsplan/20190401',
    '1',
    '2018-06-12',
    '2019-04-01',
    '24',
    '10',
    '0301',
    'Kartverket',
    '2019-04-01'
);
