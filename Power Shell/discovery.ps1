param($p1)

function Mostrar-Demo {
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host "      🔍 DISCOVERY 🔍                " -ForegroundColor Cyan
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host "🛜 O script escaneia IPs ativos dentro de uma rede." -ForegroundColor Green
    Write-Host "🔹 Ele envia pacotes ICMP e exibe os que respondem." -ForegroundColor Green
    Write-Host "🔹 Executa varredura paralela para maior desempenho." -ForegroundColor Green
    Write-Host "🔹 Exemplo de uso:" -ForegroundColor Yellow
    Write-Host "   ➤ .\script.ps1 192.168.1" -ForegroundColor Yellow
    Start-Sleep -Seconds 3
}

if (!$p1) {
    Write-Host "❌ Uso: .\script.ps1 <rede_base>" -ForegroundColor Red
    Write-Host "Exemplo: .\script.ps1 192.168.1" -ForegroundColor Yellow
    exit
}

if ($p1 -notmatch '^\d{1,3}\.\d{1,3}\.\d{1,3}$') {
    Write-Host "❌ Erro: Formato de rede inválido! Use algo como 192.168.1" -ForegroundColor Red
    exit
}

Mostrar-Demo  

Write-Host "🔍 Iniciando varredura em $p1.0/24..." -ForegroundColor Cyan
Write-Host "--------------------------------------" -ForegroundColor Cyan

$jobs = @()
foreach ($ip in 1..254) {
    $jobs += Start-Job -ScriptBlock {
        param($base, $i)
        $hostIP = "$base.$i"
        $resp = Test-Connection -Count 1 -ComputerName $hostIP -ErrorAction SilentlyContinue
        if ($resp) {
            Write-Output "[+] Host ativo: $hostIP"
        }
    } -ArgumentList $p1, $ip
}

$jobs | ForEach-Object { Receive-Job -Job $_ }
$jobs | Remove-Job

Write-Host "✅ Varredura concluída." -ForegroundColor Cyan
