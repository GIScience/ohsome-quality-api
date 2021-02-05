FROM osgeo/gdal:ubuntu-small-3.2.1

# Set C.UTF-8 locale as default (Needed by the Click library)
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get --quiet update && apt-get --quiet --yes install python3-pip

RUN useradd --create-home oqt
WORKDIR /home/oqt
USER oqt
# Create data directory
RUN mkdir --parents .local/share/oqt
# Create bin directory and add to PATH
RUN mkdir --parents /home/oqt/.local/bin
# This is needed to be able to run oqt or uvicorn commands
# without providing full path to binary of those programs
ENV PATH="/home/oqt/.local/bin:${PATH}"

COPY . .

RUN pip3 install .
