FROM debian:trixie-slim

ARG TZ="Etc/UTC"
ARG LANG="en_US.UTF-8"

ARG DEB_BUILD_DEPS="\
    build-essential \
    curl \
    git \
    python3-dev \
    unzip"

ARG DEB_PACKAGES="\
    ca-certificates \
    gdal-bin \
    libgdal-dev \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz-subset0 \
    libsqlite3-mod-spatialite \
    locales \
    tzdata"

ARG PYPI_PACKAGES="\
    gunicorn \
    jsonpatch \
    pandas \
    psycopg2-binary \    
    pydantic \
    pyld \
    pyproj \
    python-dateutil \
    PyYAML \
    shapely \
    tz"

ENV TZ=${TZ}
ENV LANG=${LANG}
ENV DEBIAN_FRONTEND="noninteractive"
ENV UV_HTTP_TIMEOUT=120
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:/root/.local/bin/:$PATH"

WORKDIR /pygeoapi
COPY . /pygeoapi

RUN \
    apt update -y \
    && apt --no-install-recommends install -y ${DEB_PACKAGES} ${DEB_BUILD_DEPS} \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8 \
    && echo "For ${TZ} date=$(date)" && echo "Locale=$(locale)" \
    && mkdir /schemas.opengis.net \
    && curl -O http://schemas.opengis.net/SCHEMAS_OPENGIS_NET.zip \
    && unzip ./SCHEMAS_OPENGIS_NET.zip "ogcapi/*" -d /schemas.opengis.net \
    && rm -f ./SCHEMAS_OPENGIS_NET.zip \    
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && uv venv $VIRTUAL_ENV \
    && uv pip install ${PYPI_PACKAGES} \
    && uv pip install gdal==$(gdal-config --version) \
    && uv pip install git+https://github.com/Arkitektum/pygeoapi.provider.postgresql_ext@main \    
    && uv pip install git+https://github.com/kartverket/DOK.Arealanalyse.Process@main \
    && uv pip install -r requirements-docker.txt \
    && uv pip install -r requirements-admin.txt \
    && uv pip install -e . \
    && cp /pygeoapi/docker/default.config.yml /pygeoapi/local.config.yml \
    && cp /pygeoapi/docker/entrypoint.sh /entrypoint.sh \
    && cd /pygeoapi \
    && for i in locale/*; do echo $i && pybabel compile -d locale -l `basename $i`; done \
    && apt remove --purge -y gcc ${DEB_BUILD_DEPS} \
    && apt clean \
    && apt autoremove -y \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]