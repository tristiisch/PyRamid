#!/bin/sh
set -eu

# Check if Docker is installed
if ! command -v docker >/dev/null 2>&1; then
	echo "Error: Docker is not installed on this system."
	exit 1
fi

# Check if service name argument is provided
if [ -z "$1" ]; then
	echo "Usage: $0 <DOCKER_SERVICE_NAME> [DOCKER_CONTEXT]"
	exit 1
fi
service_name="$1"

DOCKER_CONTEXT_ARGS=""
if [ -n "${2+set}" ]; then
	DOCKER_CONTEXT_NAME=$2
	DOCKER_CONTEXT_ARGS="--context $DOCKER_CONTEXT_NAME"
fi

# Check if the provided service exists
if ! docker $DOCKER_CONTEXT_ARGS service ps "$service_name" >/dev/null 2>&1; then
	echo "Error: The service '$service_name' does not exist."
	exit 1
fi

# Get the ID of the first running task of the Docker service
task_id=$(docker $DOCKER_CONTEXT_ARGS service ps -f "desired-state=running" -q "$service_name" | head -n 1)

# Check if no running task was found
if [ -z "$task_id" ]; then
	echo "No running task was found for the service '$service_name'."
	exit 1
fi

# Get the container ID from the task ID
container_id=$(docker $DOCKER_CONTEXT_ARGS inspect --format '{{.Status.ContainerStatus.ContainerID}}' "$task_id")

# Check if no container ID was found
if [ -z "$container_id" ]; then
	echo "No container ID was found for the running task of the service '$service_name'."
	exit 1
fi

# Connect to the first running container
docker $DOCKER_CONTEXT_ARGS exec -it "$container_id" /bin/sh
