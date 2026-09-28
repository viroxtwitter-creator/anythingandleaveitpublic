$captionWorkspace = (Resolve-Path -LiteralPath 'C:\Users\jordan\Desktop\Edit').Path
$captionPackage = Join-Path $captionWorkspace '.app-captions'
if (-not (Test-Path -LiteralPath (Join-Path $captionPackage 'CutReview\CutReview.exe'))) { throw 'New package missing' }
foreach ($oldName in @('.app-retention-v2','.app-context-sfx','.app-sfx','.app-auto','.app-ready')) {
 $oldPath=[IO.Path]::GetFullPath((Join-Path $captionWorkspace $oldName))
 $backupPath=[IO.Path]::GetFullPath((Join-Path $captionWorkspace ($oldName+'-before-captions')))
 if (-not $oldPath.StartsWith($captionWorkspace+'\') -or -not $backupPath.StartsWith($captionWorkspace+'\')) { throw 'Outside workspace' }
 if (Test-Path -LiteralPath $backupPath) { throw 'Backup already exists' }
 if (Test-Path -LiteralPath $oldPath) { Move-Item -LiteralPath $oldPath -Destination $backupPath }
 Copy-Item -LiteralPath $captionPackage -Destination $oldPath -Recurse
}
$launcherPath=Join-Path $captionWorkspace 'START CUT REVIEW.cmd'
[IO.File]::WriteAllText($launcherPath,[IO.File]::ReadAllText($launcherPath).Replace('.app-retention-v2','.app-captions'))
$captionShell=New-Object -ComObject WScript.Shell
$link=$captionShell.CreateShortcut((Join-Path $captionWorkspace 'Cut Review.lnk'))
$link.TargetPath=Join-Path $captionPackage 'CutReview\CutReview.exe'
$link.WorkingDirectory=$captionWorkspace
$link.Description='Automatic retention cuts, sound effects and Snap Captions'
$link.Save()
Write-Output 'Caption version deployed to existing shortcuts and app entry points.'
