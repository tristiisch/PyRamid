#!/bin/sh
set -eu

# Check if Docker is installed
if ! command -v docker >/dev/null 2>&1; then
  echo "Error: Docker is not installed on this system."
  exit 1
fi

# Check if service name argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <SERVICE_NAME>"
  exit 1
fi

# Check if the provided service exists
service_name="$1"
if ! docker service ps "$service_name" >/dev/null 2>&1; then
  echo "Error: The service '$service_name' does not exist."
  exit 1
fi

# Get the ID of the first running task of the Docker service
task_id=$(docker service ps -f "desired-state=running" -q "$service_name" | head -n 1)

# Check if no running task was found
if [ -z "$task_id" ]; then
  echo "No running task was found for the service '$service_name'."
  exit 1
fi

# Get the container ID from the task ID
container_id=$(docker inspect --format '{{.Status.ContainerStatus.ContainerID}}' "$task_id")

# Check if no container ID was found
if [ -z "$container_id" ]; then
  echo "No container ID was found for the running task of the service '$service_name'."
  exit 1
fi

# Connect to the first running container
docker exec -it "$container_id" /bin/sh
