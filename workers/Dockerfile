# based on Debian
FROM python:3.8

# install R
# to avoid caching issues combine apt-get update and install in one RUN statement.
# to reduce image size, clean up the apt cache by removing /var/lib/apt/lists.
RUN apt-get update && \
    apt-get install -y r-base && \
    rm -rf /var/lib/apt/lists/*

# within docker container: run without root privileges
RUN useradd -md /home/oqt oqt
WORKDIR /opt/oqt
RUN chown oqt:oqt . -R
USER oqt:oqt

# make poetry binaries available to the docker container user
ENV PATH=$PATH:/home/oqt/.local/bin

# install only the dependencies
COPY --chown=oqt:oqt pyproject.toml pyproject.toml
COPY --chown=oqt:oqt poetry.lock poetry.lock
RUN pip install --no-cache-dir poetry
RUN python -m poetry install --no-ansi --no-interaction --no-root

# copy all the other files and install the project
COPY --chown=oqt:oqt . .
RUN python -m poetry install --no-ansi --no-interaction
