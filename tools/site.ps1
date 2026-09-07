# ---------------------------------------------------------------------------
# site.ps1 - the light switch for the live site.
#
#   .\tools\site.ps1 status
#   .\tools\site.ps1 off      # take the public URL offline
#   .\tools\site.ps1 on       # put it back, same URL
#   .\tools\site.ps1 hide     # off, AND make the repo private (hides the code)
#   .\tools\site.ps1 show     # public again, then back online
#
# "off" disables GitHub Pages. The URL starts returning 404 within seconds. The
# repository stays public and browsable - only the rendered site goes away.
# Turning it back on rebuilds from main and takes about 30-60 seconds.
#
# "hide" also flips the repo to private, hiding the source as well. On a free
# account a private repo cannot serve Pages at all, so "hide" and "off" look
# the same from the URL; the difference is whether anyone can still read the
# code on github.com.
#
# Nothing here touches your commits, and the URL never changes - it is derived
# from the owner and repo name. Switch as often as you like.
#
# NOTE: this file is deliberately plain ASCII. Windows PowerShell 5.1 reads
# .ps1 as ANSI unless the file has a UTF-8 BOM, so smart quotes and dashes in
# comments corrupt the parser. Keep it ASCII.
# ---------------------------------------------------------------------------
param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'off', 'on', 'hide', 'show')]
  [string]$Action = 'status'
)

$ErrorActionPreference = 'Continue'
$Repo = 'DragonAI808/just-soccer-futsal'
$Url  = 'https://dragonai808.github.io/just-soccer-futsal/'

function Get-HttpStatus {
  # PS 5.1 has no -SkipHttpErrorCheck, so a 404 arrives as an exception and
  # the real status code has to be dug out of the response object.
  try {
    $r = Invoke-WebRequest -Uri $Url -Method Head -TimeoutSec 20 -UseBasicParsing
    return [int]$r.StatusCode
  } catch {
    if ($_.Exception.Response) { return [int]$_.Exception.Response.StatusCode }
    return 0
  }
}

function Get-PagesState {
  # When Pages is disabled the API answers 404 and gh prints the error BODY to
  # stdout, so a bare --jq .status yields that JSON rather than nothing. Match
  # on the body instead of trusting emptiness.
  $out = (gh api "repos/$Repo/pages" 2>&1 | Out-String)
  # gh exits non-zero on the 404 that means "Pages is disabled" - a correct,
  # expected answer here. Clear it, or the script reports failure after a
  # successful 'off'.
  $global:LASTEXITCODE = 0
  if ($out -match '"status"\s*:\s*"built"')    { return 'built' }
  if ($out -match '"status"\s*:\s*"building"') { return 'building' }
  if ($out -match 'Not Found')                 { return 'disabled' }
  return 'unknown'
}

function Show-State {
  $private = (gh repo view $Repo --json isPrivate --jq .isPrivate 2>$null)
  $pages   = Get-PagesState
  $code = Get-HttpStatus

  Write-Host ""
  Write-Host "  repo    : $Repo"
  Write-Host "  private : $private"
  Write-Host "  pages   : $pages"
  Write-Host "  $Url -> $code"
  if ($code -eq 200) { Write-Host "  STATE   : LIVE" -ForegroundColor Green }
  else               { Write-Host "  STATE   : OFF"  -ForegroundColor Yellow }
  Write-Host ""
}

function Wait-Build {
  Write-Host "Building (usually 30-60s)..."
  for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 8
    $st = Get-PagesState
    Write-Host ("  build: " + $st)
    if ($st -eq 'built') { return }
  }
  Write-Host "  still building - check again with: .\tools\site.ps1 status"
}

function Enable-Pages {
  gh api -X POST "repos/$Repo/pages" -f "source[branch]=main" -f "source[path]=/" 2>$null | Out-Null
}

switch ($Action) {

  'status' { Show-State }

  'off' {
    gh api -X DELETE "repos/$Repo/pages" 2>$null | Out-Null
    Write-Host "Pages disabled. Repo is still public; only the site is gone."
    Start-Sleep -Seconds 4
    Show-State
  }

  'on' {
    Enable-Pages
    Wait-Build
    Show-State
  }

  'hide' {
    gh api -X DELETE "repos/$Repo/pages" 2>$null | Out-Null
    gh repo edit $Repo --visibility private --accept-visibility-change-consequences
    Write-Host "Repo private and Pages off. Code and site both hidden."
    Start-Sleep -Seconds 4
    Show-State
  }

  'show' {
    gh repo edit $Repo --visibility public --accept-visibility-change-consequences
    Enable-Pages
    Wait-Build
    Show-State
  }
}

exit 0
