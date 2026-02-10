param(
  [string]$Tag = "main"
)

$base = "https://cdn.jsdelivr.net/gh/w2olves/epictripwithadam@$Tag/assets/poi"
$samples = @(
  @{ stateCode = "CA"; poiId = "CA_21_solvang"; index = 1 },
  @{ stateCode = "CA"; poiId = "CA_24_big_sur_coastline"; index = 1 },
  @{ stateCode = "AZ"; poiId = "AZ_01_grand_canyon_south_rim"; index = 1 }
)

foreach ($s in $samples) {
  $url = "$base/$($s.stateCode)/$($s.poiId)/$($s.index).jpg"
  try {
    $res = Invoke-WebRequest -Uri $url -Method Get -TimeoutSec 25
    "$($res.StatusCode) $url"
  } catch {
    $code = $null
    if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
      $code = [int]$_.Exception.Response.StatusCode
    }
    if ($code) {
      "$code $url"
    } else {
      "ERROR $url :: $($_.Exception.Message)"
    }
  }
}
