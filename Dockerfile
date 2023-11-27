# Builder image
# Used to retrieve information from this version
FROM python:3.12-alpine AS builder

WORKDIR /app

RUN mkdir -p src/data/functional

COPY ./src/pyramid/git.py src
COPY ./src/pyramid/data/functional/git_info.py src/data/functional

COPY ./.git/HEAD .git/HEAD
COPY ./.git/refs .git/refs
COPY ./.git/logs/HEAD ./.git/logs/HEAD
RUN python src/git.py > git_info.json

# Executable image
FROM python:3.12-alpine

LABEL org.opencontainers.image.source="https://github.com/tristiisch/PyRamid"

# Install multimedia framework that can decode, encode, transcode, mux, demux, stream, filter, and play a wide variety of multimedia files
RUN apk update
RUN apk add build-base libffi-dev openssl-dev libgcc python3-dev ffmpeg libsodium opus-dev

# Update python dependencies tool
RUN pip install --upgrade pip

# Set the working directory in the container
WORKDIR /app

# Install any necessary python dependencies
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the default config
COPY ./config.exemple.yml config.exemple.yml

# Copy git info of this build
# COPY ./git_info.json /app/git_info.json
COPY --from=builder /app/git_info.json git_info.json

# Copy the current directory contents into the container at /app
COPY ./src/pyramid src

CMD ["python", "src"]