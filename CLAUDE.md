# Dockerfile dependency pinning

The Arkitektum provider packages (postgresql_ext, mvt_postgresql_ext, styles)
create a circular dependency with this pygeoapi fork. The Dockerfile is the
integration point that controls which versions get installed together.

Version floors on shapely and pyproj in PYPI_PACKAGES and requirements.txt
prevent uv from downgrading to versions without Python 3.13 wheels during
transitive dependency resolution. If the Python version is bumped, these
floors may need updating.
