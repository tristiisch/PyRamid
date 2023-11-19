
# Builder image
# Used to retrieve information from this version
FROM python:3.11-alpine AS builder

WORKDIR /app

RUN mkdir -p src/data/functional

COPY ./src/pyramid/cli.py src
COPY ./src/pyramid/data/functional/application_info.py src/data/functional
COPY ./src/pyramid/data/functional/git_info.py src/data/functional
COPY ./src/pyramid/data/health.py src/data
COPY ./src/pyramid/client src/client
COPY ./src/pyramid/tools src/tools

COPY ./.git/HEAD .git/HEAD
COPY ./.git/refs .git/refs
COPY ./.git/logs/HEAD ./.git/logs/HEAD
RUN python src/cli.py --git > git_info.json

# Executable image
FROM python:3.11-alpine

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

HEALTHCHECK --interval=5s --retries=10 --timeout=5s CMD python ./src/cli.py health
EXPOSE 49150

CMD ["python", "src"]
