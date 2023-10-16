$ErrorActionPreference = "Stop"
$Name = "tristiisch/pyramid"
$Tag = "latest"

function Install-Requirement() {
    pip install -r .\requirements.txt
}

function Add-Lib($lib) {
    pip install $lib
    pip freeze | grep -i $lib >> requirements.txt
}

function Create-Docker() {
	docker build -t ${Name}:${Tag} .
}

function Run-Docker() {
	docker run -it ${Name}:${Tag}
}

function Push-Docker() {
	docker push ${Name}:${Tag}
}
