$ErrorActionPreference = "Stop"
$Name = "pyramid-local"
$Tag = "latest"

$RemoteName="tristiisch/pyramid"
$RemoteTag="dev"

function Install-Requirement() {
    pip install -r .\requirements.txt
}

function Add-Lib($lib) {
    pip install $lib
    pip freeze | grep -i $lib >> requirements.txt
}

function Create-Docker() {
	$data = (python src/main.py --git) -Join "`n"
	$Utf8NoBomEncoding = New-Object System.Text.UTF8Encoding $False
	[System.IO.File]::WriteAllLines(".\git_info.json", $data, $Utf8NoBomEncoding)

	docker build -t ${Name}:${Tag} .

	Remove-Item -r git_info.json
}

function Run-Docker() {
	$containerName = $Name
	# $volume = "config.yml:/app/config.yml"

	$existingContainer = docker ps -a --format '{{.Names}}' | Where-Object {$_ -eq $containerName}
	if ($existingContainer) {
		Write-Host "Container '$containerName' already exists. Stopping and removing the existing container..."
		# docker stop -t 5 $containerName
		docker rm -v -f $containerName
	}
	docker run --name $Name --mount type=bind,source=$($(Get-Item .).FullName)\config.yml,target=/app/config.yml -it ${Name}:${Tag}
}

function Push-Docker() {
	docker tag ${Name}:${Tag} ${RemoteName}/pyramid:${Tag}
	docker push ${RemoteName}/pyramid:${Tag}
}

function Clean-Docker-Image() {
	docker rmi $(docker images --filter "dangling=true" -q --no-trunc)
}

function Format-Code() {
	ruff check --fix-only --unsafe-fixes --show-fixes .\src
	ruff format .\src
}