FROM oqt-workers:latest

USER root:root
# install pg_isready to be able to check if database is ready to be used
# install java and node for sonar-scanner
RUN apt-get update && \
    apt-get install --yes --no-install-recommends postgresql-client openjdk-11-jre-headless nodejs && \
    rm -rf /var/lib/apt/lists/*

USER oqt:oqt