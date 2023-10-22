FROM python:3.11-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./src /app/src

# Copy the default config
COPY ./config.exemple.yml /app/config.exemple.yml

COPY ./requirements.txt /app/requirements.txt

COPY ./git_info.json /app/git_info.json

# Install any necessary dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install multimedia framework that can decode, encode, transcode, mux, demux, stream, filter, and play a wide variety of multimedia files
RUN apk update
RUN apk upgrade
RUN apk add --no-cache ffmpeg

CMD ["python", "src/main.py"]
