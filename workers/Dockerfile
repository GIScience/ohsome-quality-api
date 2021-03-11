FROM python:3.8

# install pg_isready to be able to check if database is ready to be used
RUN apt-get update && \
    apt-get install --yes --no-install-recommends postgresql-client && \
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