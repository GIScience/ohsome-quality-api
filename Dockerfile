# based on Debian
# we have to use bullseye, because bookworm doesn't work with older Docker versions which are still in use
FROM python:3.10-bullseye

# install R
# to avoid caching issues combine apt-get update and install in one RUN statement.
# to reduce image size, clean up the apt cache by removing /var/lib/apt/lists.
RUN apt-get update && \
    apt-get install -y r-base && \
    rm -rf /var/lib/apt/lists/*

# within docker container: run without root privileges
RUN useradd -md /home/ohsome ohsome
WORKDIR /opt/ohsome
RUN chown ohsome:ohsome . -R
USER ohsome:ohsome

# make poetry binaries available to the docker container user
ENV PATH=$PATH:/home/ohsome/.local/bin

# install only the dependencies
COPY --chown=ohsome:ohsome pyproject.toml pyproject.toml
COPY --chown=ohsome:ohsome poetry.lock poetry.lock
RUN pip install --no-cache-dir poetry
RUN python -m poetry install --no-ansi --no-interaction --no-root

# copy all the other files and install the project
COPY --chown=ohsome:ohsome ohsome_quality_api ohsome_quality_api
COPY --chown=ohsome:ohsome tests tests
COPY --chown=ohsome:ohsome scripts/start_api.py scripts/start_api.py
COPY --chown=ohsome:ohsome config/logging.yaml config/logging.yaml
RUN python -m poetry install --no-ansi --no-interaction

