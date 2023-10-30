FROM python:3.11-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./src /app/src

# Copy the default config
COPY ./config.exemple.yml /app/config.exemple.yml

# Copy git info of this build
COPY ./git_info.json /app/git_info.json

# Install any necessary python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Install multimedia framework that can decode, encode, transcode, mux, demux, stream, filter, and play a wide variety of multimedia files
RUN apk update
RUN apk add build-base libffi-dev openssl-dev libgcc python3-dev ffmpeg libsodium opus-dev

CMD ["python", "src/main.py"]
