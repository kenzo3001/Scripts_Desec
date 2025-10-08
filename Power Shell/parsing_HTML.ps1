# Função para exibir a explicação antes de rodar
function mostrar_demo {
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "            🌐 PARSING HTML 🌐          " -ForegroundColor Yellow
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "➡️  O script obtém informações do servidor e os métodos HTTP aceitos."
    Write-Host "➡️  Além disso, extrai todos os links encontrados na página."
    Write-Host "➡️  Basta fornecer a URL completa (exemplo: http://exemplo.com)."
    Write-Host "=========================================" -ForegroundColor Cyan
    Start-Sleep -Seconds 3
}

mostrar_demo

$site = Read-Host "Digite a URL completa (ex: http://site.com)"

try {
    # Obtendo os headers
    $options = Invoke-WebRequest -Uri "$site" -Method Options -ErrorAction Stop

    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host " 🖥️  Servidor identificado:" -ForegroundColor Green
    if ($options.Headers.Server) {
        Write-Host "   $($options.Headers.Server)" -ForegroundColor White
    } else {
        Write-Host "   ❌ Não informado pelo servidor." -ForegroundColor Red
    }

    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host " 📡 Métodos HTTP aceitos:" -ForegroundColor Green
    if ($options.Headers.Allow) {
        Write-Host "   $($options.Headers.Allow)" -ForegroundColor White
    } else {
        Write-Host "   ❌ O servidor não forneceu informações." -ForegroundColor Red
    }

    # Obtendo o conteúdo da página
    $web = Invoke-WebRequest -Uri "$site" -Method Get -ErrorAction Stop

    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host " 🔗 Links encontrados na página: " -ForegroundColor Green
    if ($web.Links.Count -gt 0) {
        foreach ($link in $web.Links) {
            Write-Host "   - $($link.href)" -ForegroundColor White
        }
    } else {
        Write-Host "   ❌ Nenhum link encontrado." -ForegroundColor Red
    }

} catch {
    Write-Host "`n❌ Ocorreu um erro ao processar a URL: $_" -ForegroundColor Red
}
