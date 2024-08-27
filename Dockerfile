# Define the Python version and other build arguments
ARG PYTHON_VERSION=3.12
ARG PROJECT_VERSION=0.0.0
ARG APP_USER=app-usr
ARG APP_GROUP=app-grp

# ============================ Builder Image ============================
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
    # Only for ARM64 architecture
    if [ "$(uname -m)" = "aarch64" ]; then \
        apk update && \
        apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev; \
    fi && \
    # Install Python dependencies
    pip install --no-cache-dir -r requirements.txt && \
    # Clean up build dependencies for ARM64 architecture
    if [ "$(uname -m)" = "aarch64" ]; then \
        apk del .build-deps; \
    fi

# ============================ Base Image ============================
FROM python:$PYTHON_VERSION-alpine AS base

ARG APP_USER
ARG APP_GROUP
ARG PROJECT_VERSION
ENV PROJECT_VERSION=$PROJECT_VERSION

# Install necessary dependencies
RUN apk update && \
    apk upgrade && \
    apk add --no-cache ffmpeg opus-dev binutils && \
    # Clean up apk cache
    ls -lah /var/cache/apk/ && \
    rm -rf /var/cache/apk/*

WORKDIR /app

# Create a user and group for running the application
RUN addgroup -g 1000 -S $APP_GROUP && adduser -u 1000 -S $APP_USER -G $APP_GROUP

# Create and set permissions for directories
RUN mkdir -p ./songs && chmod 770 ./songs && chown root:$APP_GROUP ./songs && \
    mkdir -p ./logs && chmod 770 ./logs && chown root:$APP_GROUP ./logs

# ============================ Executable Image ============================
FROM base AS executable

ARG PROJECT_VERSION
ARG APP_USER
ARG APP_GROUP

LABEL org.opencontainers.image.source="https://github.com/tristiisch/PyRamid" \
      org.opencontainers.image.authors="tristiisch" \
      version="$PROJECT_VERSION"

# Copy the virtual environment from the builder stage
COPY --chown=root:$APP_GROUP --chmod=550 --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application sources into the container
COPY --chown=root:$APP_GROUP --chmod=750 ./src ./src
COPY --chown=root:$APP_GROUP --chmod=550 ./setup.py ./setup.py

# Create project information folder and set permissions
RUN mkdir -p ./src/pyramid.egg-info && \
    chmod 770 -R ./src/pyramid.egg-info && \
    chown $APP_USER:$APP_GROUP -R ./src/pyramid.egg-info

# Install the project
RUN pip install -e .

# Switch to the non-root user
USER $APP_USER

HEALTHCHECK --interval=30s --retries=3 --timeout=30s CMD python ./src/cli.py health

# Expose port for health check
EXPOSE 49150

CMD ["python", "./src"]

# ============================ Builder Dev Image ============================
FROM builder AS builder-dev

COPY ./requirements-dev.txt requirements-dev.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

# ============================ Test Image ============================
FROM base AS tests

ARG APP_GROUP
ARG APP_USER
WORKDIR /app

# Copy the virtual environment and sources for testing
COPY --chown=root:$APP_GROUP --chmod=550 --from=builder-dev /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --chown=root:$APP_GROUP --chmod=750 ./src ./src
COPY --chown=root:$APP_GROUP --chmod=750 ./tests ./tests
COPY --chown=root:$APP_GROUP --chmod=550 ./setup.py ./setup.py

# Create and set permissions for project information folder
RUN mkdir -p ./src/pyramid.egg-info && \
    chmod 770 -R ./src/pyramid.egg-info && \
    chown $APP_USER:$APP_GROUP -R ./src/pyramid.egg-info && \
    chown $APP_USER:$APP_GROUP . && \
    chmod 770 .

# Install the project
RUN pip install -e .

# Switch to the non-root user
USER $APP_USER

# Run tests
CMD ["pytest", "--cov=pyramid tests/", "--cov-config=.coveragerc"]
