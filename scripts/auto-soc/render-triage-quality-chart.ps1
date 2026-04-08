param(
    [string]$CsvPath,
    [string]$OutPath,
    [int]$LastN = 30
)

$OpsRoot = if ($env:OPS_ROOT) { $env:OPS_ROOT } else { "C:\RH\OPS" }
$ReportsDir = Join-Path $OpsRoot "50_System/Runs/Reports"
if (-not $CsvPath) { $CsvPath = Join-Path $ReportsDir "autosoc-triage-quality-history.csv" }
if (-not $OutPath) { $OutPath = Join-Path $ReportsDir "autosoc-triage-quality-trend.png" }

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $CsvPath)) {
    throw "CSV not found: $CsvPath"
}

$rows = Import-Csv -LiteralPath $CsvPath
if (-not $rows -or $rows.Count -eq 0) {
    throw "CSV has no data rows: $CsvPath"
}

$parsed = foreach ($r in $rows) {
    [PSCustomObject]@{
        generated_utc = [datetime]::Parse($r.generated_utc)
        window_hours = [int]$r.window_hours
        current_cases = [double]$r.current_cases
        current_escalated = [double]$r.current_escalated
        current_review = [double]$r.current_review
        current_auto_closed_benign = [double]$r.current_auto_closed_benign
        current_auto_closed_known_fp = [double]$r.current_auto_closed_known_fp
        current_escalation_rate_pct = [double]$r.current_escalation_rate_pct
        delta_escalation_rate_pct = [double]$r.delta_escalation_rate_pct
    }
}

$seriesRows = $parsed | Sort-Object generated_utc | Select-Object -Last $LastN

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Windows.Forms.DataVisualization

$chart = New-Object System.Windows.Forms.DataVisualization.Charting.Chart
$chart.Width = 1600
$chart.Height = 900
$chart.BackColor = [System.Drawing.Color]::FromArgb(10, 18, 32)

$area = New-Object System.Windows.Forms.DataVisualization.Charting.ChartArea "main"
$area.BackColor = [System.Drawing.Color]::FromArgb(17, 26, 46)
$area.AxisX.LabelStyle.ForeColor = [System.Drawing.Color]::Gainsboro
$area.AxisY.LabelStyle.ForeColor = [System.Drawing.Color]::Gainsboro
$area.AxisY2.LabelStyle.ForeColor = [System.Drawing.Color]::Gainsboro
$area.AxisX.MajorGrid.LineColor = [System.Drawing.Color]::FromArgb(38, 54, 82)
$area.AxisY.MajorGrid.LineColor = [System.Drawing.Color]::FromArgb(38, 54, 82)
$area.AxisY2.MajorGrid.LineColor = [System.Drawing.Color]::FromArgb(38, 54, 82)
$area.AxisY2.Enabled = "True"
$area.AxisY.Title = "Escalation Rate (%)"
$area.AxisY2.Title = "Case Volume"
$area.AxisY.TitleForeColor = [System.Drawing.Color]::Gainsboro
$area.AxisY2.TitleForeColor = [System.Drawing.Color]::Gainsboro
$area.AxisX.IntervalAutoMode = "VariableCount"
$area.AxisX.LabelStyle.Angle = -30
$chart.ChartAreas.Add($area)

$title = New-Object System.Windows.Forms.DataVisualization.Charting.Title
$title.Text = "AutoSOC Triage Quality Trend"
$title.ForeColor = [System.Drawing.Color]::White
$title.Font = New-Object System.Drawing.Font("Segoe UI", 18, [System.Drawing.FontStyle]::Bold)
$chart.Titles.Add($title)

$subTitle = New-Object System.Windows.Forms.DataVisualization.Charting.Title
$subTitle.Text = "Escalation Rate vs Case Volume (recent runs)"
$subTitle.ForeColor = [System.Drawing.Color]::LightGray
$subTitle.Font = New-Object System.Drawing.Font("Segoe UI", 11, [System.Drawing.FontStyle]::Regular)
$subTitle.Docking = "Top"
$chart.Titles.Add($subTitle)

$legend = New-Object System.Windows.Forms.DataVisualization.Charting.Legend
$legend.Docking = "Bottom"
$legend.ForeColor = [System.Drawing.Color]::Gainsboro
$legend.BackColor = [System.Drawing.Color]::FromArgb(10, 18, 32)
$chart.Legends.Add($legend)

$rateSeries = New-Object System.Windows.Forms.DataVisualization.Charting.Series "Escalation Rate %"
$rateSeries.ChartType = "Line"
$rateSeries.BorderWidth = 3
$rateSeries.Color = [System.Drawing.Color]::FromArgb(98, 169, 255)
$rateSeries.MarkerStyle = "Circle"
$rateSeries.MarkerSize = 6
$rateSeries.YAxisType = "Primary"

$caseSeries = New-Object System.Windows.Forms.DataVisualization.Charting.Series "Cases"
$caseSeries.ChartType = "Column"
$caseSeries.Color = [System.Drawing.Color]::FromArgb(88, 201, 140)
$caseSeries.YAxisType = "Secondary"
$caseSeries["PointWidth"] = "0.55"

$deltaSeries = New-Object System.Windows.Forms.DataVisualization.Charting.Series "Escalation Delta (pts)"
$deltaSeries.ChartType = "Line"
$deltaSeries.BorderDashStyle = "Dash"
$deltaSeries.BorderWidth = 2
$deltaSeries.Color = [System.Drawing.Color]::FromArgb(255, 184, 77)
$deltaSeries.MarkerStyle = "Diamond"
$deltaSeries.MarkerSize = 5
$deltaSeries.YAxisType = "Primary"

foreach ($row in $seriesRows) {
    $label = $row.generated_utc.ToString("MM-dd HH:mm")
    [void]$rateSeries.Points.AddXY($label, $row.current_escalation_rate_pct)
    [void]$caseSeries.Points.AddXY($label, $row.current_cases)
    [void]$deltaSeries.Points.AddXY($label, $row.delta_escalation_rate_pct)
}

$chart.Series.Add($caseSeries)
$chart.Series.Add($rateSeries)
$chart.Series.Add($deltaSeries)

$chart.AntiAliasing = "All"
$chart.TextAntiAliasingQuality = "High"

$outDir = Split-Path -Path $OutPath -Parent
if (-not (Test-Path -LiteralPath $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

$chart.SaveImage($OutPath, "Png")

Write-Output "QUALITY_CHART_PNG=$OutPath"
Write-Output ("POINTS_RENDERED={0}" -f $seriesRows.Count)
