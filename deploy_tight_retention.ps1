$workspacePath = (Resolve-Path -LiteralPath 'C:\Users\jordan\Desktop\Edit').Path
$packagePath = Join-Path $workspacePath '.app-retention-v2'
if (-not (Test-Path -LiteralPath (Join-Path $packagePath 'CutReview\CutReview.exe'))) { throw 'New package missing' }
foreach ($oldName in @('.app-context-sfx','.app-sfx','.app-auto','.app-ready')) {
    $oldPath = [IO.Path]::GetFullPath((Join-Path $workspacePath $oldName))
    $backupPath = [IO.Path]::GetFullPath((Join-Path $workspacePath ($oldName + '-before-tight-retention')))
    if (-not $oldPath.StartsWith($workspacePath + '\') -or -not $backupPath.StartsWith($workspacePath + '\')) { throw 'Outside workspace' }
    if (Test-Path -LiteralPath $backupPath) { throw 'Backup already exists' }
    if (Test-Path -LiteralPath $oldPath) { Move-Item -LiteralPath $oldPath -Destination $backupPath }
    Copy-Item -LiteralPath $packagePath -Destination $oldPath -Recurse
}
$launcherPath = Join-Path $workspacePath 'START CUT REVIEW.cmd'
$launcherText = [IO.File]::ReadAllText($launcherPath).Replace('.app-context-sfx','.app-retention-v2')
[IO.File]::WriteAllText($launcherPath,$launcherText)
$shellLink = New-Object -ComObject WScript.Shell
$link = $shellLink.CreateShortcut((Join-Path $workspacePath 'Cut Review.lnk'))
$link.TargetPath = Join-Path $packagePath 'CutReview\CutReview.exe'
$link.WorkingDirectory = $workspacePath
$link.Description = 'Tight speech, retake removal, shooting checks and varied SFX'
$link.Save()
Write-Output 'Updated launcher, shortcut and previous app entry points.'
