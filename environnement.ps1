$ErrorActionPreference = "Stop"


function Install-Requirement() {
    pip install -r .\requirements.txt
}

function Add-Lib($lib) {
    pip install $lib
    pip freeze | grep -i $lib >> requirements.txt
}

