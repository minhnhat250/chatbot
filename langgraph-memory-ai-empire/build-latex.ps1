param(
    [string]$MainTex = "main.tex",
    [switch]$Fast,
    [switch]$DraftOnly
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = (Resolve-Path -LiteralPath $projectRoot).Path
$buildRoot = Join-Path $projectRoot "build"
$envRoot = Join-Path $projectRoot ".tex-env"
$miktexRoot = Join-Path $envRoot "miktex"
$miktexConfig = Join-Path $miktexRoot "config"
$miktexData = Join-Path $miktexRoot "data"
$miktexInstall = Join-Path $miktexRoot "install"
$miktexConfigLeaf = Join-Path $miktexConfig "miktex\config"
$miktexSourceConfig = "D:\MiKTeX\miktex\config"
$miktexBin = "D:\MiKTeX\miktex\bin\x64"

New-Item -ItemType Directory -Force -Path `
    $buildRoot, (Join-Path $buildRoot "sections"), `
    $miktexConfigLeaf, $miktexData, $miktexInstall | Out-Null

if (-not (Test-Path -LiteralPath (Join-Path $miktexConfigLeaf "scripts.ini"))) {
    Copy-Item -Path (Join-Path $miktexSourceConfig "*") `
        -Destination $miktexConfigLeaf -Recurse -Force
}

# Use MiKTeX-specific environment variables. Do not override HOME, USERPROFILE,
# APPDATA or other user-profile variables.
$env:MIKTEX_USERCONFIG = $miktexConfig
$env:MIKTEX_USERDATA = $miktexData
$env:MIKTEX_USERINSTALL = $miktexInstall
$env:PATH = "$miktexBin;$env:PATH"

$initexmf = (Get-Command initexmf.exe -ErrorAction Stop).Source
$initArgs = @(
    "--user-config=$miktexConfig"
    "--user-data=$miktexData"
    "--user-install=$miktexInstall"
    "--user-roots=D:\MiKTeX"
    "--report"
)
& $initexmf @initArgs | Out-Null

$generatedPatterns = @(
    "*.aux", "*.toc", "*.out", "*.bcf", "*.run.xml",
    "*.blg", "*.log", "*.lof", "*.lot"
)
foreach ($pattern in $generatedPatterns) {
    Get-ChildItem -LiteralPath $buildRoot -Filter $pattern -File `
        -ErrorAction SilentlyContinue | Remove-Item -Force
}
Get-ChildItem -LiteralPath (Join-Path $buildRoot "sections") `
    -Filter "*.aux" -File -ErrorAction SilentlyContinue | Remove-Item -Force

$pdflatex = (Get-Command pdflatex.exe -ErrorAction Stop).Source
$biber = (Get-Command biber.exe -ErrorAction Stop).Source
$jobName = [IO.Path]::GetFileNameWithoutExtension($MainTex)

Push-Location $projectRoot
try {
    $firstPassArgs = @(
        "-interaction=nonstopmode"
        "-halt-on-error"
        "-file-line-error"
        "-recorder"
        "-output-directory=build"
    )
    if ($DraftOnly) {
        $firstPassArgs += "-draftmode"
    }
    $firstPassArgs += $MainTex

    & $pdflatex @firstPassArgs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    if ($DraftOnly) {
        exit 0
    }

    if (-not $Fast) {
        & $biber --input-directory=build --output-directory=build $jobName
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }

    & $pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -recorder `
        -output-directory=build $MainTex
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    & $pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -recorder `
        -output-directory=build $MainTex
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
