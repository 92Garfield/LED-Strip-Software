# Pulls the shared js/ and css/ from the Chrome extension, which is the
# source of truth for everything except manifest.json.
$chrome = Join-Path $PSScriptRoot "..\gLED-Client Chrome"
Remove-Item -Recurse -Force (Join-Path $PSScriptRoot "js"), (Join-Path $PSScriptRoot "css") -ErrorAction SilentlyContinue
Copy-Item -Recurse (Join-Path $chrome "js"), (Join-Path $chrome "css") $PSScriptRoot
Write-Host "Synced js/ and css/ from gLED-Client Chrome."
