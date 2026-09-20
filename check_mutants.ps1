$ErrorActionPreference = "Stop"
Write-Host "==> Running Mutmut with Hypothesis 'mutation' profile..."
$env:HYPOTHESIS_PROFILE = "mutation"
mutmut run

mutmut results

$res = mutmut results | Out-String
if ($res -match "(\d+)\s+survived") {
    $surviving = [int]$matches[1]
    if ($surviving -gt 0) {
        Write-Host "[-] Quality Gate Failed: $surviving mutant(s) survived." -ForegroundColor Red
        Write-Host "Inspect with: mutmut show <id>"
        exit 1
    }
}

Write-Host "[+] 100% Mutation score achieved! All properties killed injected mutants." -ForegroundColor Green
exit 0
