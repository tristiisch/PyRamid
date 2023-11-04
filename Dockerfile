FROM python:3.11-alpine

# Install multimedia framework that can decode, encode, transcode, mux, demux, stream, filter, and play a wide variety of multimedia files
RUN apk update
RUN apk add build-base libffi-dev openssl-dev libgcc python3-dev ffmpeg libsodium opus-dev

# Update python dependencies tool
RUN pip install --upgrade pip

# Set the working directory in the container
WORKDIR /app

# Install any necessary python dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Copy the default config
COPY ./config.exemple.yml /app/config.exemple.yml

# Copy git info of this build
COPY ./git_info.json /app/git_info.json

# Copy the current directory contents into the container at /app
COPY ./src /app/src

CMD ["python", "src/pyramid"]
