# Define the Python version to be used
ARG PYTHON_VERSION=3.12
ARG VERSION=0.0.0
ARG GIT_COMMIT_ID=0000000
ARG GIT_BRANCH=unknown
ARG GIT_LAST_AUTHOR=unknown
ARG APP_USER=app-usr
ARG APP_GROUP=app-grp

# <===================================> Image info <===================================>
FROM python:$PYTHON_VERSION-alpine AS info

ARG GIT_COMMIT_ID
ARG GIT_BRANCH
ARG GIT_LAST_AUTHOR

WORKDIR /app

# Generate the git_info.json file
RUN EOF=$(dd if=/dev/urandom bs=15 count=1 status=none | base64 -w 0) && \
    cat <<$EOF > git_info.json
{
    "commit_id": "$GIT_COMMIT_ID",
    "branch": "$GIT_BRANCH",
    "last_author": "$GIT_LAST_AUTHOR"
}
$EOF

# <===================================> Builder image <===================================>
FROM python:$PYTHON_VERSION-alpine AS builder

WORKDIR /app

# Install dependencies necessary for building Python packages
# Use only for arch linux/arm64/v8
RUN if [ "$(uname -m)" = "aarch64" ]; then \
        apk update && \
		apk add --no-cache gcc musl-dev libffi-dev; \
    fi

# Install virtual environment
RUN python -m venv /opt/venv

# Add the virtual environment to the PATH
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip to the latest version
RUN pip install --no-cache-dir --upgrade pip

# Install Python dependencies for the application
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# <===================================> Executable image <===================================>
FROM python:$PYTHON_VERSION-alpine AS executable

ARG VERSION
ARG GIT_COMMIT_ID
ARG APP_USER
ARG APP_GROUP

# Label for the image source
LABEL org.opencontainers.image.source="https://github.com/tristiisch/PyRamid"
LABEL org.opencontainers.image.authors="tristiisch"
LABEL version="$VERSION-$GIT_COMMIT_ID"

# Install necessary dependencies
RUN apk update && \
    apk upgrade && \
    apk add --no-cache ffmpeg opus-dev binutils && \
    rm -rf /var/cache/apk/* /etc/apk/cache/* /root/.cache/*

# Set the working directory in the container
WORKDIR /app

# Create a user and group for running the application
RUN addgroup -S $APP_GROUP && adduser -S $APP_USER -G $APP_GROUP

# Copy entrypoint script and set permissions
COPY --chown=root:$APP_GROUP --chmod=550 entrypoint.sh /usr/local/bin/

# Copy the default config
COPY --chown=root:$APP_GROUP --chmod=550 ./config.exemple.yml config.exemple.yml

# Create directory for downloaded songs
RUN mkdir -p ./songs && chmod -R 770 ./songs && chown -R root:$APP_GROUP ./songs
RUN mkdir -p ./logs && chmod -R 770 ./logs && chown -R root:$APP_GROUP ./logs

# Copy the virtual environment from the builder stage
COPY --chown=root:$APP_GROUP --chmod=550 --from=builder /opt/venv /opt/venv

# Copy git info of this build
COPY --chown=root:$APP_GROUP --chmod=550 --from=info /app/git_info.json git_info.json

# Copy the current directory contents into the container at /app
COPY --chown=root:$APP_GROUP --chmod=750 ./src ./src
COPY --chown=root:$APP_GROUP --chmod=550 ./setup.py ./setup.py

RUN mkdir -p src/pyramid.egg-info \
	&& chmod 770 -R ./src/pyramid.egg-info \
	&& chown $APP_USER:$APP_GROUP -R ./src/pyramid.egg-info

# Switch to the non-root user
USER $APP_USER

RUN pip install -e .

# Add the virtual environment to the PATH
ENV PATH="/opt/venv/bin:$PATH"

HEALTHCHECK --interval=30s --retries=3 --timeout=30s CMD python ./src/cli.py health
# Socket port for external health
EXPOSE 49150

# Define the entrypoint and default command
ENTRYPOINT ["entrypoint.sh"]
CMD ["python", "src"]
