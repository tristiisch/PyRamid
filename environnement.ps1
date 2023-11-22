$ErrorActionPreference = "Stop"
$LocalName = "pyramid-local"
$LocalTag = "latest"

$RemoteName="tristiisch/pyramid"
$RemoteTag="dev"

function Install-Requirement() {
	pip install --upgrade -r .\requirements.txt
}

function Add-Lib($lib) {
	pip install $lib

	$version = (pip freeze | Select-String -Pattern "$lib==" -CaseSensitive -SimpleMatch).Line -replace "$lib=="
	$higherMajorVersion = "$([int]($version -Split "\." | Select-Object -First 1) + 1).0.0"
	$newVersionSpecifier = "$lib>=$version,<$higherMajorVersion"
	Write-Output $newVersionSpecifier | Out-File -Append -FilePath requirements.txt
}

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