$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime]
$null = [Windows.Storage.Streams.IRandomAccessStream, Windows.Storage.Streams, ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.SoftwareBitmap, Windows.Graphics.Imaging, ContentType=WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime]
$null = [Windows.Media.Ocr.OcrResult, Windows.Foundation, ContentType=WindowsRuntime]
$null = [Windows.Globalization.Language, Windows.Globalization, ContentType=WindowsRuntime]
$asTask = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' } | Select-Object -First 1
function Wait-WinRT($operation, [Type]$resultType) {
 $task = $asTask.MakeGenericMethod($resultType).Invoke($null, @($operation))
 $task.Wait()
 return $task.Result
}
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage([Windows.Globalization.Language]::new('ar-SA'))
if (!$engine) { throw 'Arabic OCR unavailable' }
$root = Split-Path -Parent $PSScriptRoot
$source = Join-Path $root 'content/sources/heavy-originals'
$results = @()
foreach ($image in Get-ChildItem -LiteralPath $source -Filter '*.png' -File | Sort-Object Name) {
 $file = Wait-WinRT ([Windows.Storage.StorageFile]::GetFileFromPathAsync($image.FullName)) ([Windows.Storage.StorageFile])
 $stream = Wait-WinRT ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
 try {
  $decoder = Wait-WinRT ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
  $bitmap = Wait-WinRT ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
  try {
   $result = Wait-WinRT ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
   $lines = @($result.Lines | ForEach-Object { [pscustomobject]@{ text=$_.Text; words=@($_.Words | ForEach-Object { [pscustomobject]@{text=$_.Text;x=$_.BoundingRect.X;y=$_.BoundingRect.Y;width=$_.BoundingRect.Width;height=$_.BoundingRect.Height} }) } })
   $results += [pscustomobject]@{id=$image.BaseName;text=$result.Text;lines=$lines}
  } finally { $bitmap.Dispose() }
 } finally { $stream.Dispose() }
 if ($results.Count % 20 -eq 0) { Write-Output "OCR: $($results.Count) images" }
}
[IO.File]::WriteAllText((Join-Path $source 'ocr.json'),($results | ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))
Write-Output "Saved $($results.Count) OCR records for review; no answer keys inferred."
