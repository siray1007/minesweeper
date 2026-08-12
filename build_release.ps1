$ErrorActionPreference = 'Stop'

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$buildDir = Join-Path $projectDir 'build_temp'
$distDir = Join-Path $buildDir 'dist'
$workDir = Join-Path $buildDir 'work'
$specDir = Join-Path $buildDir 'spec'
$appName = [string]([char]0x626B) + [char]0x96F7
$iconName = $appName + [char]0x56FE + [char]0x6807
$outputExe = Join-Path $projectDir ($appName + '.exe')

$pyInstallerLocation = (& python -c "import site; print(site.getusersitepackages())").Trim()
if (-not $pyInstallerLocation) {
    throw 'PyInstaller is not installed for the active Python interpreter.'
}
if (-not (Test-Path -LiteralPath (Join-Path $pyInstallerLocation 'PyInstaller'))) {
    throw "PyInstaller package not found under $pyInstallerLocation"
}

New-Item -ItemType Directory -Force -Path $distDir, $workDir, $specDir | Out-Null

$dataFiles = @(
    'bomb16.png',
    'bomb24.png',
    'bomb32.png',
    'bomb_transparent.png',
    ($iconName + '.png')
)

$arguments = @(
    (Join-Path $projectDir 'build_pyinstaller.py'),
    "--pyinstaller-path=$pyInstallerLocation",
    '--noconfirm',
    '--clean',
    '--onefile',
    '--windowed',
    '--name', $appName,
    '--icon', (Join-Path $projectDir ($iconName + '.ico')),
    '--distpath', $distDir,
    '--workpath', $workDir,
    '--specpath', $specDir
)

foreach ($file in $dataFiles) {
    $arguments += '--add-data'
    $arguments += "$(Join-Path $projectDir $file);."
}

$arguments += (Join-Path $projectDir 'main.py')
& python @arguments
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}

Copy-Item -LiteralPath (Join-Path $distDir ($appName + '.exe')) -Destination $outputExe -Force
$item = Get-Item -LiteralPath $outputExe
Write-Host "Release ready: $($item.FullName) ($($item.Length) bytes)"
