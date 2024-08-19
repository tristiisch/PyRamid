# Define the Python version to be used
ARG PYTHON_VERSION=3.12
ARG VERSION=0.0.0
ARG GIT_COMMIT_ID=0000000
ARG GIT_BRANCH=unknown
ARG GIT_LAST_AUTHOR=unknown
ARG APP_USER=app-usr
ARG APP_GROUP=app-grp

# <===================================> Builder image <===================================>
FROM python:$PYTHON_VERSION-alpine AS builder

WORKDIR /building

RUN \
	# Install virtual environment
	python -m venv /opt/venv && \
	# Upgrade pip to the latest version
	pip install --no-cache-dir --upgrade pip

# Add the virtual environment to the PATH
ENV PATH="/opt/venv/bin:$PATH"

# Copy dependencies list 
COPY ./requirements.txt requirements.txt

RUN \
	# Install dependencies necessary for building Python packages
	# Use only for arch linux/arm64
	if [ "$(uname -m)" = "aarch64" ]; then \
        apk update && \
		apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev; \
    fi && \
	# Install Python dependencies for the application
	pip install --no-cache-dir -r requirements.txt && \
	if [ "$(uname -m)" = "aarch64" ]; then \
		apk remove .build-deps; \
    fi

# <===================================> Base image <===================================>
FROM python:$PYTHON_VERSION-alpine AS base

ARG APP_USER
ARG APP_GROUP

# Install necessary dependencies
RUN apk update && \
    apk upgrade && \
    apk add --no-cache ffmpeg opus-dev binutils && \
    rm -rf /var/cache/apk/* /etc/apk/cache/* /root/.cache/*

# Set the working directory in the container
WORKDIR /app

# Create a user and group for running the application
RUN addgroup -S $APP_GROUP && adduser -S $APP_USER -G $APP_GROUP

# Create directory for downloaded songs
RUN mkdir -p ./songs && chmod -R 770 ./songs && chown -R root:$APP_GROUP ./songs
RUN mkdir -p ./logs && chmod -R 770 ./logs && chown -R root:$APP_GROUP ./logs

# <===================================> Executable image <===================================>
FROM base AS executable

ARG VERSION
ARG GIT_COMMIT_ID
ARG APP_USER
ARG APP_GROUP

# Label for the image source
LABEL org.opencontainers.image.source="https://github.com/tristiisch/PyRamid"
LABEL org.opencontainers.image.authors="tristiisch"
LABEL version="$VERSION-$GIT_COMMIT_ID"

# Copy the virtual environment from the builder stage
COPY --chown=root:$APP_GROUP --chmod=550 --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the current directory contents into the container at /app
COPY --chown=root:$APP_GROUP --chmod=750 ./src ./src
COPY --chown=root:$APP_GROUP --chmod=550 ./setup.py ./setup.py

RUN mkdir -p ./src/pyramid.egg-info && \
	chmod 770 -R ./src/pyramid.egg-info && \
	chown $APP_USER:$APP_GROUP -R ./src/pyramid.egg-info

# Switch to the non-root user
USER $APP_USER

RUN pip install -e .

HEALTHCHECK --interval=30s --retries=3 --timeout=30s CMD python ./src/cli.py health
# Socket port for external health
EXPOSE 49150

# Define the entrypoint and default command
ENTRYPOINT entrypoint.sh
CMD ["python", "./src"]

# <===================================> Builder Dev image <===================================>
FROM builder AS builder-dev

COPY ./requirements-dev.txt requirements-dev.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

# <===================================> Test image <===================================>
FROM base AS tests

ARG APP_GROUP
ARG APP_USER
WORKDIR /app

COPY --chown=root:$APP_GROUP --chmod=550 --from=builder-dev /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --chown=root:$APP_GROUP --chmod=750 ./src ./src
COPY --chown=root:$APP_GROUP --chmod=750 ./tests ./tests
COPY --chown=root:$APP_GROUP --chmod=550 ./setup.py ./setup.py

RUN mkdir -p ./src/pyramid.egg-info && \
	chmod 770 -R ./src/pyramid.egg-info && \
	chown $APP_USER:$APP_GROUP -R ./src/pyramid.egg-info && \
	chown $APP_USER:$APP_GROUP . && \
	chmod 770 .

RUN pip install -e .

USER $APP_USER
CMD pip freeze && pytest --cov=pyramid tests/
