$ErrorActionPreference = "Stop"
$LocalName = "pyramid-local"
$LocalTag = "latest"

$RemoteName="tristiisch/pyramid"
$RemoteTag="dev"


function Create-Docker() {
	$data = (python src/pyramid --git) -Join "`n"
	$Utf8NoBomEncoding = New-Object System.Text.UTF8Encoding $False
	[System.IO.File]::WriteAllLines(".\git_info.json", $data, $Utf8NoBomEncoding)

	docker build -t ${LocalName}:${LocalTag} .

	Remove-Item -r git_info.json
}

function Run-Docker() {
	$containerName = $LocalName
	# $volume = "config.yml:/app/config.yml"

	$existingContainer = docker ps -a --format '{{.Names}}' | Where-Object {$_ -eq $containerName}
	if ($existingContainer) {
		Write-Host "Container '$containerName' already exists. Stopping and removing the existing container..."
		# docker stop -t 5 $containerName
		docker rm -v -f $containerName
	}
	docker run --name $LocalName `
		--mount type=bind,source=$($(Get-Item .).FullName)\config.yml,target=/app/config.yml `
		-it ${LocalName}:${LocalTag}
}

function Push-Docker() {
	docker tag ${LocalName}:${LocalTag} ${RemoteName}:${RemoteTag}
	docker push ${RemoteName}:${RemoteTag}
}

function Clean-Docker-Image() {
	docker rmi $(docker images --filter "dangling=true" -q --no-trunc)
}

function Format-Code() {
	ruff check --fix-only --unsafe-fixes --show-fixes .\src
	ruff format .\src
}

function Clean-Python-Cache() {
	$Path = "./src"
	$DirToDelete = Get-ChildItem -Path $Path -Recurse -Directory | Where-Object { $_.Name -eq "__pycache__" }
	$DirToDelete | ForEach-Object { Remove-Item -Recurse -Force $_.FullName }
	Write-Host "$($DirToDelete.Length) directories of Python cache have been deleted."
}

function Get-Container-IP($containerName) {
	# Get the container object by name
	$container_id = docker ps -qf "name=$containerName"

	# Check if the container exists
	if ($null -eq $container_id) {
		Write-Host "Container $containerName not found."
		return $null
	} else {
		# Get the network settings for the container
		# Extract the private IP address
		$privateIP = docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $container_id

		return $privateIP
	}
}
function Test-Health-Docker-Compose() {
	$containerName = "pyramid"
	# $ip = Get-Container-IP $containerName
	$ip = "localhost"
	python.exe .\src\pyramid\cli.py health --host $ip --port 49149
}
