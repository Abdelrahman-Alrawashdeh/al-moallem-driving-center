$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$projectRoot = Split-Path -Parent $PSScriptRoot
$distRoot = (Resolve-Path -LiteralPath (Join-Path $projectRoot 'dist')).Path
$outputPath = Join-Path $projectRoot 'al-moallem-cloudflare.zip'
$stream = [System.IO.File]::Open($outputPath, [System.IO.FileMode]::Create)
$archive = [System.IO.Compression.ZipArchive]::new($stream, [System.IO.Compression.ZipArchiveMode]::Create)
try {
  foreach ($file in Get-ChildItem -LiteralPath $distRoot -Recurse -File | Where-Object { $_.Name -notin @('desktop.ini', 'Thumbs.db', '.DS_Store') }) {
    # ZIP paths must use forward slashes, including when built on Windows.
    $entryName = $file.FullName.Substring($distRoot.Length + 1).Replace('\', '/')
    $entry = $archive.CreateEntry($entryName, [System.IO.Compression.CompressionLevel]::Optimal)
    $inputStream = [System.IO.File]::OpenRead($file.FullName)
    $entryStream = $entry.Open()
    try { $inputStream.CopyTo($entryStream) }
    finally { $entryStream.Dispose(); $inputStream.Dispose() }
  }
} finally { $archive.Dispose(); $stream.Dispose() }

$archive = [System.IO.Compression.ZipFile]::OpenRead($outputPath)
try {
  $entries = @{}
  foreach ($entry in $archive.Entries) {
    if ($entry.FullName.Contains('\')) { throw "Invalid ZIP separator: $($entry.FullName)" }
    $entries[$entry.FullName] = $entry
    $localPath = Join-Path $distRoot $entry.FullName
    $entryStream = $entry.Open()
    $localStream = [System.IO.File]::OpenRead($localPath)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
      $zipHash = [Convert]::ToBase64String($sha.ComputeHash($entryStream))
      $localHash = [Convert]::ToBase64String($sha.ComputeHash($localStream))
      if ($zipHash -ne $localHash) { throw "Corrupt asset: $($entry.FullName)" }
    } finally { $sha.Dispose(); $entryStream.Dispose(); $localStream.Dispose() }
  }
  if (!$entries.ContainsKey('index.html')) { throw 'Missing root index.html' }
  foreach ($document in Get-ChildItem -LiteralPath $distRoot -Filter '*.html' -Recurse -File) {
    $html = [System.IO.File]::ReadAllText($document.FullName)
    $references = [regex]::Matches($html, '(?:src|href)="(/[^"#]+)"')
    foreach ($reference in $references) {
      $assetPath = $reference.Groups[1].Value.Split('?')[0].TrimStart('/')
      if (!$entries.ContainsKey($assetPath)) { throw "Referenced asset missing from ZIP: $assetPath" }
    }
  }
  $bankPath = Join-Path $distRoot 'data/question-bank.json'
  if (Test-Path -LiteralPath $bankPath) {
    $bank = [System.IO.File]::ReadAllText($bankPath) | ConvertFrom-Json
    foreach ($question in $bank.questions) {
      if ($question.image -and !$entries.ContainsKey($question.image.TrimStart('/'))) {
        throw "Question image missing from ZIP: $($question.image)"
      }
    }
  }
  Write-Output "PASS: $($entries.Count) files verified by SHA-256; all local HTML assets present; portable ZIP paths."
  Write-Output "Ready to upload: $outputPath"
} finally { $archive.Dispose() }
