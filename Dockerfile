FROM osgeo/gdal:ubuntu-small-latest

# Set C.UTF-8 locale as default (Needed by the Click library)
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ARG YOUR_ENV

ENV YOUR_ENV=${YOUR_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.1.4 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  PATH="$PATH:/root/.poetry/bin"

# Install pip
RUN apt-get update
RUN apt-get --yes install python3-pip
RUN apt-get --yes install git

RUN pip3 install "poetry==$POETRY_VERSION"

WORKDIR /root

# Create directories for config, data and logs
RUN mkdir --parents .local/share/oqt

# Copy mapswipe workers repo from local repo
COPY . .

RUN poetry config virtualenvs.create false
RUN poetry install  --no-dev


