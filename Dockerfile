# based on Debian
# we have to use bullseye, because bookworm doesn't work with older Docker versions which are still in use
FROM python:3.10-bullseye

# Allow to set custom uid and gid values (i.e. for CI)
ARG uid=1000
ARG gid=1000

# install R
# to avoid caching issues combine apt-get update and install in one RUN statement.
# to reduce image size, clean up the apt cache by removing /var/lib/apt/lists.
RUN apt-get update && \
    apt-get install -y r-base && \
    rm -rf /var/lib/apt/lists/*

# within docker container: run without root privileges
RUN groupadd -g "$gid" oqapi
RUN useradd -l -md /home/oqapi -u "$uid" -g "$gid" oqapi
WORKDIR /opt/oqapi
RUN pip install --no-cache-dir poetry
RUN chown oqapi:oqapi . -R
USER oqapi:oqapi

# make poetry binaries available to the docker container user
ENV PATH=$PATH:/home/oqapi/.local/bin

# install only the dependencies
COPY --chown=oqapi:oqapi pyproject.toml pyproject.toml
COPY --chown=oqapi:oqapi poetry.lock poetry.lock
RUN python -m poetry install --no-ansi --no-interaction --no-root

# copy all the other files and install the project
COPY --chown=oqapi:oqapi ohsome_quality_api ohsome_quality_api
COPY --chown=oqapi:oqapi tests tests
COPY --chown=oqapi:oqapi scripts/start_api.py scripts/start_api.py
COPY --chown=oqapi:oqapi config/logging.yaml config/logging.yaml
RUN python -m poetry install --no-ansi --no-interaction

