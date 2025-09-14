Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$base = 'http://127.0.0.1:8001'
$s = New-Object Microsoft.PowerShell.Commands.WebRequestSession

Write-Host 'Warm up and fetch CSRF...'
Invoke-WebRequest -UseBasicParsing -WebSession $s -Uri "$base/login/" -Method GET | Out-Null
$csrf = ($s.Cookies.GetCookies($base) | Where-Object { $_.Name -eq 'csrftoken' } | Select-Object -First 1).Value
if (-not $csrf) { Write-Error 'No CSRF token found'; exit 1 }

Write-Host 'Attempting registration (idempotent)...'
$reg = @{ name='Smoke Tester'; email='smoke_tester@example.com'; password='test1234'; confirm_password='test1234'; mobile='9999999999'; college='DDA'; passout_year='2025'; branch='CSE'; csrfmiddlewaretoken=$csrf }
try { Invoke-WebRequest -UseBasicParsing -WebSession $s -Uri "$base/register/" -Method POST -Body $reg -Headers @{Referer="$base/register/"} | Out-Null } catch { }

Write-Host 'Logging in...'
Invoke-WebRequest -UseBasicParsing -WebSession $s -Uri "$base/login/" -Method GET | Out-Null
$csrf = ($s.Cookies.GetCookies($base) | Where-Object { $_.Name -eq 'csrftoken' } | Select-Object -First 1).Value
$login = @{ email='smoke_tester@example.com'; password='test1234'; csrfmiddlewaretoken=$csrf }
$respLogin = Invoke-WebRequest -UseBasicParsing -WebSession $s -Uri "$base/login/" -Method POST -Body $login -Headers @{Referer="$base/login/"} -MaximumRedirection 5

Write-Host 'Fetching problems...'
$problemsResp = Invoke-WebRequest -UseBasicParsing -WebSession $s -Uri "$base/api/problems/" -Method GET
$problems = ($problemsResp.Content | ConvertFrom-Json).problems
if (-not $problems -or $problems.Count -eq 0) { Write-Error 'No problems available to test'; exit 2 }
$problemId = $problems[0].id
Write-Host "Using problem id: $problemId"

Write-Host 'Opening problem page to refresh CSRF...'
Invoke-WebRequest -UseBasicParsing -WebSession $s -Uri "$base/problems/$problemId/" -Method GET | Out-Null
$csrf = ($s.Cookies.GetCookies($base) | Where-Object { $_.Name -eq 'csrftoken' } | Select-Object -First 1).Value

Write-Host 'Submitting code via run_code...'
$code = @'
def solution(*args, **kwargs):
    return 0
'@
$body = @{ code=$code; language='python'; action='run'; csrfmiddlewaretoken=$csrf }
$runResp = Invoke-WebRequest -UseBasicParsing -WebSession $s -Uri "$base/run_code/$problemId/" -Method POST -Body $body -Headers @{ 'X-CSRFToken'=$csrf; 'Referer'="$base/problems/$problemId/" }
$runJson = $runResp.Content | ConvertFrom-Json
$subId = $runJson.submission_id
if (-not $subId) { Write-Error ("No submission_id returned. Raw: {0}" -f $runResp.Content); exit 3 }
Write-Host "Created submission: $subId"

Write-Host 'Polling submission status...'
$max = 20
for ($i=0; $i -lt $max; $i++) {
  Start-Sleep -Seconds 1
  $st = Invoke-WebRequest -UseBasicParsing -WebSession $s -Uri "$base/api/submissions/$subId/" -Method GET
  $j = $st.Content | ConvertFrom-Json
  Write-Host ("Status: {0} (t={1}s)" -f $j.status, ($i+1))
  if ($j.status -eq 'DONE' -or $j.status -eq 'ERROR') {
    $j | ConvertTo-Json -Depth 6 | Write-Host
    if ($j.status -eq 'DONE') { exit 0 } else { exit 4 }
  }
}
Write-Error 'Timed out waiting for submission'
exit 5
