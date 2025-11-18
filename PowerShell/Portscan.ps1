param(
    [Parameter(Mandatory = $true)]
    [string]$ip,

    [Parameter(Mandatory = $false)]
    [int[]]$ports = @(21, 22, 25, 80, 443, 3306, 445),

    [switch]$showClosed,

    [string]$outputFile
)

function Mostrar-Demo {
    Write-Host "`nExemplo de uso:" -ForegroundColor Yellow
    Write-Host "powershell -File scanner.ps1 -ip 192.168.0.1"
    Write-Host "powershell -File scanner.ps1 -ip 10.0.0.1 -ports 80,443,8080 -showClosed"
    Write-Host "powershell -File scanner.ps1 -ip 172.16.1.1 -outputFile resultado.txt`n"
}

function Registrar-Saida {
    param($mensagem)
    if ($outputFile) {
        Add-Content -Path $outputFile -Value $mensagem
    }
}

Write-Host "`n🔎 Iniciando varredura de portas em $ip ..." -ForegroundColor Cyan
Registrar-Saida "`nResultado do scan em $ip:`n"

foreach ($porta in $ports) {
    try {
        $aberta = Test-NetConnection -ComputerName $ip -Port $porta -WarningAction SilentlyContinue -InformationLevel Quiet
        if ($aberta) {
            $msg = "✅ Porta $porta: Aberta"
            Write-Host $msg -ForegroundColor Green
            Registrar-Saida $msg
        } elseif ($showClosed) {
            $msg = "❌ Porta $porta: Fechada"
            Write-Host $msg -ForegroundColor Red
            Registrar-Saida $msg
        }
    } catch {
        $msg = "⚠️  Erro ao testar a porta $porta. Verifique IP ou conexão."
        Write-Host $msg -ForegroundColor Yellow
        Registrar-Saida $msg
    }
}

Write-Host "`n✅ Scan finalizado.`n" -ForegroundColor Cyan
Registrar-Saida "`nScan finalizado em $(Get-Date)`n"
