$ErrorActionPreference = "Stop"
$requirementFile = ".\requirements.txt"

class PythonLibrary {
    [string]$Name
    [string]$Smallest_Version_Symbol
    [string]$Smallest_Version
    [string]$Biggest_Version_Symbol
    [string]$Biggest_Version
    [string]$Extra

    PythonLibrary([string]$Name, [string]$Smallest_Version_Symbol, [string]$Smallest_Version, [string]$Biggest_Version_Symbol, [string]$Biggest_Version, [string]$Extra) {
        $this.Name = $Name
        $this.Smallest_Version_Symbol = $Smallest_Version_Symbol
        $this.Smallest_Version = $Smallest_Version
        $this.Biggest_Version_Symbol = $Biggest_Version_Symbol
        $this.Biggest_Version = $Biggest_Version
        $this.Extra = $Extra
    }
}

function Install-Requirement() {
	pip install --upgrade -r $requirementFile
}

function Get-Libs($content) {
    $libObjects = @()
	$regex = "^(?<name>[a-zA-Z0-9_.\-]+)(?<smal_ver_symb>>=|==)(?<smal_ver>[^,;\s]*)(,(?<big_ver_symb><)(?<big_ver>[^,;\s]*))?(\s*;\s*(?<extra>.+))?$"

    foreach ($line in $content) {

		if (!($line -match $regex)) {
			Write-Host "Unknown '" + $line + "'"
		}
		$name = $matches["name"]
		$smal_ver_symb = $matches["smal_ver_symb"]
		$smal_ver = $matches["smal_ver"]
		$big_ver_symb = $matches["big_ver_symb"]
		$big_ver = $matches["big_ver"]
		$extra = $matches["extra"]

        $libObject = [PythonLibrary]::new($name, $smal_ver_symb, $smal_ver, $big_ver_symb, $big_ver, $extra)

        $libObjects += $libObject
    }

    return $libObjects
}

function Save-Libs([PythonLibrary[]]$libObjects) {
	$requirementFile = $requirementFile
    try {
        $data = $libObjects | ForEach-Object {
            $line = "$($_.Name)$($_.Smallest_Version_Symbol)$($_.Smallest_Version)"
            if ($null -ne $_.Biggest_Version_Symbol) {
                $line += ",$($_.Biggest_Version_Symbol)$($_.Biggest_Version)"
            }
            if ($null -Ne $_.Extra -And "" -Ne $_.Extra ) {
                $line += "; $($_.Extra)"
            }
            $line
        }
		[System.IO.File]::WriteAllLines($requirementFile, $data)
        Write-Host "Libraries saved to $requirementFile" -ForegroundColor Green
    }
    catch {
        Write-Host "Error: $_" -ForegroundColor Red
    }
}

function Get-Requirement-Libs() {
    $lines = Get-Content $requirementFile
    $libObjects = Get-Libs $lines

    return $libObjects
}

function Get-Local-Libs() {
    $lines = pip freeze
    $libObjects = Get-Libs $lines

    return $libObjects
}

function Find-Libs([PythonLibrary[]]$libObjects, [string]$libName) {
    $itemFind = $libObjects | Where-Object { $libName.ToLower() -eq $_.Name.ToLower() }
	return $itemFind
}

function Find-Libs([PythonLibrary[]]$libObjects, [PythonLibrary[]]$libObjects2) {
    $itemFind = $libObjects | Where-Object { $libObjects2.Name.ToLower() -eq $_.Name.ToLower() }
	return $itemFind
}

function Get-Local-Requirement-Libs() {
    $localLibs = Get-Local-Libs
    $requirementLibs = Get-Requirement-Libs
	$localRequirementLibs = Find-Libs $localLibs $requirementLibs

    return $localRequirementLibs
}

function Update-Libs() {
	Install-Requirement
	$requirementLibs = Get-Requirement-Libs
	$localRequirementLibs = Get-Local-Requirement-Libs
	$requirementLibsToUpdate = $requirementLibs | Where-Object {
		$item = $_
		$matchingItem = Find-Libs $localRequirementLibs $item
		$matchingItem.Smallest_Version -Ne $_.Smallest_Version
	}
	if ($requirementLibsToUpdate.count -Eq 0) {
		Write-Host "They is no update" -ForegroundColor Red
		return
	}
	Write-Host "Libraries updated :" -ForegroundColor Green
	foreach ($requirementLibToUpdate in $requirementLibsToUpdate) {
		$localLib = Find-Libs $localRequirementLibs $requirementLibToUpdate
		Write-Host $requirementLibToUpdate.Name $requirementLibToUpdate.Smallest_Version "->" $localLib.Smallest_Version

		$requirementLibToUpdate.Smallest_Version = $localLib.Smallest_Version
	}

	Save-Libs $requirementLibs
}

function Format-Requirement-Lib([PythonLibrary]$libObject) {
	$libObject.Smallest_Version_Symbol = ">="

	$higherMajorVersion = "$([int]($libObject.Smallest_Version -Split "\." | Select-Object -First 1) + 1).0.0"
	$libObject.Biggest_Version_Symbol = "<"
	$libObject.Biggest_Version = $higherMajorVersion
}

function Add-Lib([string]$libName) {
    $localLibs = Get-Local-Libs
    $requirementLibs = Get-Requirement-Libs

	$local = Find-Libs $localLibs $libName
	$requirement = Find-Libs $requirementLibs $libName

	if ($Null -Ne $local) {
		Write-Host "Library $($local.Name) is already installed on local files with version" `
			"$($local.Smallest_Version_Symbol) $($local.Smallest_Version)" -ForegroundColor Red
	} else {
		pip install $libName
		$localLibs = Get-Local-Libs
		$local = Find-Libs $localLibs $libName
	}

	if ($Null -Ne $requirement) {
		Write-Host "Library $($requirement.Name) is already defined on $requirementFile with version" `
			"$($requirement.Smallest_Version_Symbol) $($requirement.Smallest_Version)" -ForegroundColor Red
	} else {
		Format-Requirement-Lib $local
		$requirementLibs += $local
		Save-Libs $requirementLibs
	}
}

function Remove-Lib([string]$libName) {
    $localLibs = Get-Local-Libs
    $requirementLibs = Get-Requirement-Libs

	$local = Find-Libs $localLibs $libName
	$requirement = Find-Libs $requirementLibs $libName

	if ($Null -Eq $local) {
		Write-Host "Library $libName is not installed on local files." -ForegroundColor Red
	} else {
		pip uninstall -y $($local.Name)
		if (!($?)) {
			return
		}
		$localLibs = Get-Local-Libs
		$local = Find-Libs $localLibs $libName
	}

	if ($Null -Eq $requirement) {
		Write-Host "Library $libName is not defined on $requirementFile." -ForegroundColor Red
	} else {
		$requirementLibs | Where-Object { $_.FieldName -Ne $requirement.Name }
		Save-Libs $requirementLibs
	}
}
