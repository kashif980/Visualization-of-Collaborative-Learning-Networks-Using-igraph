$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$preferredPython = "C:\ProgramData\anaconda3\python.exe"
Set-Location $projectRoot

if (Test-Path $preferredPython) {
    & $preferredPython -m http.server 8620
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    python -m http.server 8620
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    py -m http.server 8620
} else {
    throw "Python or the py launcher was not found on PATH."
}
