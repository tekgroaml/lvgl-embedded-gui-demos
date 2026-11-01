<#
.SYNOPSIS
Collect this Windows PC's real CPU/RAM and optional NVIDIA metrics.
No Python/pip is needed. Optional Pi upload requires configured OpenSSH key
access (BatchMode); passwords/tokens are never arguments or stored here.
#>
[CmdletBinding()]
param(
    [string]$OutputFile = (Join-Path $env:LOCALAPPDATA 'Tekgroaml\pc-monitor.json'),
    [ValidateRange(1,60)][int]$IntervalSeconds = 2,
    [ValidateRange(0,15)][int]$GpuIndex = 0,
    [string]$PiTarget,
    [switch]$Once
)
$ErrorActionPreference = 'Stop'
$utf8 = New-Object System.Text.UTF8Encoding($false)
$culture = [System.Globalization.CultureInfo]::InvariantCulture

function Read-Number([object]$Value) {
    if ($null -eq $Value) { return $null }
    $parsed = 0.0
    if ([double]::TryParse([string]$Value, [System.Globalization.NumberStyles]::Float, $culture, [ref]$parsed)) {
        if (-not [double]::IsNaN($parsed) -and -not [double]::IsInfinity($parsed)) { return $parsed }
    }
    return $null
}

function Read-PcSnapshot {
    $processor = Get-CimInstance Win32_PerfFormattedData_PerfOS_Processor -Filter "Name='_Total'"
    $operatingSystem = Get-CimInstance Win32_OperatingSystem
    $cpu = Read-Number $processor.PercentProcessorTime
    if ($null -eq $cpu) { throw 'CPU utilization is unavailable.' }
    $total = [double]$operatingSystem.TotalVisibleMemorySize / 1048576
    $used = ([double]$operatingSystem.TotalVisibleMemorySize - [double]$operatingSystem.FreePhysicalMemory) / 1048576
    if ($total -le 0 -or $used -lt 0 -or $used -gt $total) { throw 'RAM metrics are unavailable.' }
    $data = [ordered]@{
        schema_version = 1
        sampled_at = 0
        pc_name = ([string]$env:COMPUTERNAME).Substring(0, [Math]::Min(32, ([string]$env:COMPUTERNAME).Length))
        workload = 'LIVE PC'
        cpu_load_pct = [Math]::Min(100, [Math]::Max(0, $cpu))
        memory_used_gb = [Math]::Round($used, 3)
        memory_total_gb = [Math]::Round($total, 3)
        cpu_temp_c = $null
        cpu_power_w = $null
        gpu_load_pct = $null
        gpu_temp_c = $null
        gpu_power_w = $null
        vram_used_gb = $null
        vram_total_gb = $null
        cpu_fan_rpm = $null
        gpu_fan_rpm = $null
        download_mbps = $null
        upload_mbps = $null
    }
    $nvidia = Get-Command nvidia-smi -ErrorAction SilentlyContinue
    if ($nvidia) {
      try {
        $rows = @(& $nvidia.Source "--id=$GpuIndex" '--query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total' '--format=csv,noheader,nounits' 2>$null)
        if ($LASTEXITCODE -eq 0 -and $rows.Count -eq 1) {
            $values = ([string]$rows[0]).Split(',')
            if ($values.Count -eq 4) {
                $data.gpu_load_pct = Read-Number $values[0]
                $data.gpu_temp_c = Read-Number $values[1]
                $vramUsed = Read-Number $values[2]
                $vramTotal = Read-Number $values[3]
                if ($null -ne $vramUsed -and $null -ne $vramTotal -and $vramTotal -gt 0 -and $vramUsed -ge 0 -and $vramUsed -le $vramTotal) {
                    $data.vram_used_gb = [Math]::Round($vramUsed / 1024, 3)
                    $data.vram_total_gb = [Math]::Round($vramTotal / 1024, 3)
                }
            }
        }
        $power = @(& $nvidia.Source "--id=$GpuIndex" '--query-gpu=power.draw' '--format=csv,noheader,nounits' 2>$null)
        if ($LASTEXITCODE -eq 0 -and $power.Count -eq 1) { $data.gpu_power_w = Read-Number $power[0] }
        # nvidia-smi fan.speed is a percentage, not RPM. Never put it in *_rpm.
      } catch {
        # Unsupported/failed optional GPU probes do not fabricate values or
        # prevent genuine CPU/RAM collection from continuing.
      }
    }
    $data.sampled_at = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() / 1000.0
    return $data
}

$OutputFile = [System.IO.Path]::GetFullPath($OutputFile)
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($OutputFile)) | Out-Null
if ($PiTarget) {
    if ($PiTarget -notmatch '^[a-zA-Z0-9_][a-zA-Z0-9_.-]*@[a-zA-Z0-9][a-zA-Z0-9_.-]*$') { throw 'Use a simple user@hostname or user@IPv4 PiTarget.' }
    foreach ($command in @('ssh','scp')) {
        if (-not (Get-Command $command -ErrorAction SilentlyContinue)) { throw "Missing Windows OpenSSH command: $command" }
    }
    & ssh -o BatchMode=yes -o ConnectTimeout=5 $PiTarget 'mkdir -p ~/.local/state/pc-monitor'
    if ($LASTEXITCODE -ne 0) { throw 'SSH key login/known host must be configured before Pi upload.' }
}

do {
    try {
        $data = Read-PcSnapshot
        $temporary = $OutputFile + '.tmp'
        [System.IO.File]::WriteAllText($temporary, ($data | ConvertTo-Json -Depth 4), $utf8)
        if ([System.IO.File]::Exists($OutputFile)) {
            [System.IO.File]::Replace($temporary, $OutputFile, $null)
        } else {
            [System.IO.File]::Move($temporary, $OutputFile)
        }
        if ($PiTarget) {
            & scp -q -o BatchMode=yes -o ConnectTimeout=5 $OutputFile "${PiTarget}:.local/state/pc-monitor/input.json.new"
            if ($LASTEXITCODE -ne 0) { throw 'PC snapshot upload failed.' }
            & ssh -o BatchMode=yes -o ConnectTimeout=5 $PiTarget 'mv -f ~/.local/state/pc-monitor/input.json.new ~/.local/state/pc-monitor/input.json'
            if ($LASTEXITCODE -ne 0) { throw 'PC snapshot publish failed.' }
        }
        Write-Host ('PC snapshot updated: ' + $OutputFile)
    } catch {
        Write-Warning $_.Exception.Message
        if ($Once) { throw }
        # No synthetic fallback. The Pi will display stale/unavailable data.
    }
    if (-not $Once) { Start-Sleep -Seconds $IntervalSeconds }
} while (-not $Once)
