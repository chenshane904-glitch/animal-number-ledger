# 自动触发并监控 macOS 构建
# 使用方法：请先设置你的 GitHub Token
# $env:GITHUB_TOKEN = "your_token_here"
# .\trigger_build.ps1

$REPO = "chenshane904-glitch/animal-number-ledger"
$WORKFLOW = "build-macos.yml"
$BRANCH = "macos-packaging"

# 检查是否设置了 GitHub Token
if (-not $env:GITHUB_TOKEN) {
    Write-Host "错误：请先设置 GitHub Token" -ForegroundColor Red
    Write-Host "运行: `$env:GITHUB_TOKEN = 'your_token_here'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "获取 Token：https://github.com/settings/tokens" -ForegroundColor Cyan
    Write-Host "需要权限：repo, workflow" -ForegroundColor Cyan
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $env:GITHUB_TOKEN"
    "Accept" = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}

Write-Host "=== 触发 macOS 构建 ===" -ForegroundColor Green
Write-Host "仓库: $REPO"
Write-Host "分支: $BRANCH"
Write-Host ""

# 触发工作流
$body = @{
    ref = $BRANCH
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod `
        -Uri "https://api.github.com/repos/$REPO/actions/workflows/$WORKFLOW/dispatches" `
        -Method Post `
        -Headers $headers `
        -Body $body `
        -ContentType "application/json"

    Write-Host "✓ 工作流已触发" -ForegroundColor Green
    Write-Host ""
    Start-Sleep -Seconds 5
} catch {
    Write-Host "✗ 触发失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 监控构建状态
Write-Host "=== 监控构建状态 ===" -ForegroundColor Green
Write-Host "等待构建开始..."
Write-Host ""

$maxAttempts = 60
$attempt = 0

while ($attempt -lt $maxAttempts) {
    try {
        # 获取最新的工作流运行
        $runs = Invoke-RestMethod `
            -Uri "https://api.github.com/repos/$REPO/actions/workflows/$WORKFLOW/runs?branch=$BRANCH&per_page=1" `
            -Headers $headers

        if ($runs.workflow_runs.Count -gt 0) {
            $run = $runs.workflow_runs[0]
            $status = $run.status
            $conclusion = $run.conclusion
            $runId = $run.id

            $timestamp = Get-Date -Format "HH:mm:ss"

            if ($status -eq "completed") {
                Write-Host ""
                Write-Host "=== 构建完成 ===" -ForegroundColor Green
                Write-Host "结果: $conclusion"
                Write-Host "Run ID: $runId"
                Write-Host ""

                if ($conclusion -eq "success") {
                    Write-Host "✓ 构建成功！" -ForegroundColor Green
                    Write-Host ""
                    Write-Host "下载 Artifacts：" -ForegroundColor Cyan
                    Write-Host "https://github.com/$REPO/actions/runs/$runId"
                    exit 0
                } else {
                    Write-Host "✗ 构建失败：$conclusion" -ForegroundColor Red
                    Write-Host ""
                    Write-Host "查看日志：" -ForegroundColor Cyan
                    Write-Host "https://github.com/$REPO/actions/runs/$runId"
                    exit 1
                }
            } else {
                Write-Host "[$timestamp] 状态: $status" -ForegroundColor Yellow
            }
        }

        Start-Sleep -Seconds 30
        $attempt++
    } catch {
        Write-Host "✗ 查询失败: $($_.Exception.Message)" -ForegroundColor Red
        Start-Sleep -Seconds 30
        $attempt++
    }
}

Write-Host ""
Write-Host "✗ 超时：30分钟内未完成" -ForegroundColor Red
Write-Host "请手动检查：https://github.com/$REPO/actions"
