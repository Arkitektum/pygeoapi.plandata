# Dockerfile dependency pinning

The Arkitektum provider packages (postgresql_ext, mvt_postgresql_ext, styles)
create a circular dependency with this pygeoapi fork. The Dockerfile is the
integration point that controls which versions get installed together.

Each `uv pip install` call resolves dependencies independently, so version
pins in PYPI_PACKAGES don't prevent downgrades in later install steps. The
Dockerfile freezes the environment after installing PYPI_PACKAGES and passes
it via `--constraint` to the Arkitektum package installs. This prevents uv
from downgrading packages like shapely and pyproj to versions without
Python 3.13 wheels when resolving transitive dependencies.

Version floors on shapely (>=2.1.0) and pyproj (>=3.7.0) in PYPI_PACKAGES
and requirements.txt serve as documentation of minimum Python 3.13-compatible
versions. If the Python version is bumped, these floors may need updating.
