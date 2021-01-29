FROM osgeo/gdal:ubuntu-small-3.2.1

# Set C.UTF-8 locale as default (Needed by the Click library)
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get -q update && apt-get -q --yes install python3-pip

RUN useradd --create-home oqt
WORKDIR /home/oqt
USER oqt
# Create data and bin directories
RUN mkdir --parents .local/share/oqt
RUN mkdir --parents .local/bin
ENV PATH="/home/opt/.local/bin:${PATH}"

COPY pyproject.toml .
COPY ohsome_quality_tool ohsome_quality_tool

RUN pip3 install .
