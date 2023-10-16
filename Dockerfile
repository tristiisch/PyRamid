# Use the official Python 3.11 image as the base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./src /app/src

# Copy the default config
COPY ./config.exemple.yml /app/config.exemple.yml

COPY ./requirements.txt /app/requirements.txt

# Install any necessary dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install multimedia framework that can decode, encode, transcode, mux, demux, stream, filter, and play a wide variety of multimedia files
RUN apt update
RUN apt install ffmpeg -y

CMD ["python", "src/main.py"]
