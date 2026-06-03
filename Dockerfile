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
    libsqlite3-mod-spatialite \
    locales \
    tzdata"

ARG PYPI_PACKAGES="\
    gunicorn \
    gevent \
    jsonpatch \
    pandas \
    psycopg2-binary \    
    pydantic \
    pyld \
    pyproj>=3.7.0 \
    python-dateutil \
    PyYAML \
    shapely>=2.1.0 \
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
    && uv pip freeze > /tmp/constraints.txt \
    && uv pip install --constraint /tmp/constraints.txt git+https://github.com/Arkitektum/pygeoapi.provider.postgresql_ext@v0.5.0 \
    && uv pip install --constraint /tmp/constraints.txt git+https://github.com/Arkitektum/pygeoapi.provider.mvt_postgresql_ext@main \
    && uv pip install --constraint /tmp/constraints.txt git+https://github.com/Arkitektum/pygeoapi.provider.styles@main \
    && uv pip install --constraint /tmp/constraints.txt git+https://github.com/Arkitektum/pygeoapi.formatter.gml-npad@v0.3.0 \
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