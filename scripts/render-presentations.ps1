$ErrorActionPreference = 'Stop'
$workspaceRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$catalog = Get-Content -LiteralPath (Join-Path $workspaceRoot 'content/presentations/extracted.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$application = $null
try {
  $application = New-Object -ComObject PowerPoint.Application
  $application.AutomationSecurity = 3
  foreach ($deck in $catalog) {
    $sourcePath = Join-Path $workspaceRoot $deck.file
    $outputDirectory = Join-Path $workspaceRoot ('content/presentations/rendered/' + $deck.id)
    [System.IO.Directory]::CreateDirectory($outputDirectory) | Out-Null
    $presentation = $null
    try {
      $presentation = $application.Presentations.Open($sourcePath, -1, 0, 0)
      $height = [int][Math]::Round(1280 * $presentation.PageSetup.SlideHeight / $presentation.PageSetup.SlideWidth)
      foreach ($slide in $presentation.Slides) {
        $targetPath = Join-Path $outputDirectory ('slide-{0:D3}.png' -f $slide.SlideIndex)
        $slide.Export($targetPath, 'PNG', 1280, $height)
      }
      Write-Output "$($deck.id): exported $($presentation.Slides.Count) slides."
    } finally { if ($presentation) { $presentation.Close(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($presentation) } }
  }
} finally { if ($application) { $application.Quit(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($application) } }
