$ErrorActionPreference = "Stop"
$Name = "pyramid-local"
$Tag = "latest"

function Install-Requirement() {
    pip install -r .\requirements.txt
}

function Add-Lib($lib) {
    pip install $lib
    pip freeze | grep -i $lib >> requirements.txt
}

function Create-Docker() {
	python src/main.py --git > git_info.json
	docker build -t ${Name}:${Tag} .
	Remove-Item -r git_info.json
}

function Run-Docker() {
	docker run -it ${Name}:${Tag}
}

function Push-Docker() {
	docker push ${Name}:${Tag}
}
